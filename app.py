import joblib
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Churn / Signal",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Theme is presentation-only; the prediction pipeline below is unchanged.
header_col, theme_col = st.columns([5, 1], vertical_alignment="center")
with theme_col:
    dark_mode = st.toggle("Dark mode", value=False)

if dark_mode:
    palette = {
        "page": "#171916",
        "surface": "#20231F",
        "surface_alt": "#282C27",
        "text": "#F2EFE7",
        "muted": "#A9ADA3",
        "line": "#41463E",
        "accent": "#E6A15A",
        "accent_text": "#171916",
        "field": "#252923",
    }
else:
    palette = {
        "page": "#F3F0E8",
        "surface": "#FBFAF6",
        "surface_alt": "#EAE6DC",
        "text": "#252720",
        "muted": "#73766D",
        "line": "#D7D2C7",
        "accent": "#D85B3F",
        "accent_text": "#FFFFFF",
        "field": "#FFFFFF",
    }

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    :root {{
        --page: {palette['page']};
        --surface: {palette['surface']};
        --surface-alt: {palette['surface_alt']};
        --ink: {palette['text']};
        --muted: {palette['muted']};
        --line: {palette['line']};
        --accent: {palette['accent']};
        --accent-ink: {palette['accent_text']};
        --field: {palette['field']};
    }}

    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background: var(--page);
        color: var(--ink);
    }}
    [data-testid="stAppViewContainer"] {{ background: var(--page); }}
    [data-testid="stHeader"] {{ background: transparent; }}
    .block-container {{
        max-width: 1180px;
        padding: 1.25rem 2.1rem 2rem;
    }}
    h1, h2, h3, [data-testid="stMetricValue"] {{
        color: var(--ink) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.045em;
    }}
    p, label, .stMarkdown, [data-testid="stCaptionContainer"] {{
        color: var(--ink);
        font-family: 'DM Sans', sans-serif;
    }}
    .eyebrow, .section-kicker, .metric-label {{
        color: var(--accent);
        font-family: 'DM Mono', monospace;
        font-size: .68rem;
        font-weight: 500;
        letter-spacing: .12em;
        text-transform: uppercase;
    }}
    .hero-title {{
        color: var(--ink);
        font: 700 clamp(2.35rem, 5.4vw, 4.4rem)/.98 'Space Grotesk', sans-serif;
        letter-spacing: -.065em;
        margin: .35rem 0 .65rem;
    }}
    .hero-copy {{
        color: var(--muted);
        font: 400 1rem/1.55 'DM Sans', sans-serif;
        max-width: 620px;
        margin: 0;
    }}
    .hero-meta {{
        border-left: 1px solid var(--line);
        padding: .35rem 0 .35rem 1rem;
        color: var(--muted);
        font: 500 .7rem/1.9 'DM Mono', monospace;
        letter-spacing: .07em;
        text-transform: uppercase;
    }}
    .hero-meta strong {{
        display: block;
        color: var(--ink);
        font: 600 1rem/1.4 'Space Grotesk', sans-serif;
        letter-spacing: -.02em;
        text-transform: none;
    }}
    .section-kicker {{ margin: .1rem 0 .25rem; }}
    .section-note, .small-print {{
        color: var(--muted);
        font: 400 .82rem/1.45 'DM Sans', sans-serif;
    }}
    .section-note {{ margin: 0 0 .65rem; }}
    .metric-label {{ margin-bottom: .2rem; }}
    .metric-value {{ color: var(--ink); font: 600 1rem 'Space Grotesk', sans-serif; }}
    div[data-testid="stForm"] {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 3px;
        padding: 1rem 1.15rem .9rem;
    }}
    div[data-testid="stSelectbox"] label,
    div[data-testid="stNumberInput"] label,
    div[data-testid="stSlider"] label {{
        color: var(--muted) !important;
        font-size: .78rem;
        font-weight: 600;
    }}
    div[data-baseweb="select"] > div,
    div[data-testid="stNumberInput"] input {{
        background: var(--field);
        border-color: var(--line);
        color: var(--ink);
        border-radius: 3px;
        min-height: 2.35rem;
    }}
    div[data-testid="stSlider"] [data-baseweb="slider"] {{ padding-top: .25rem; }}
    div[data-testid="stSlider"] [role="slider"] {{ background: var(--accent); border-color: var(--accent); }}
    div[data-testid="stFormSubmitButton"] button {{
        min-height: 2.75rem;
        border: 1px solid var(--accent);
        border-radius: 3px;
        background: var(--accent);
        color: var(--accent-ink);
        font: 700 .9rem 'DM Sans', sans-serif;
        transition: filter .15s ease, transform .15s ease;
    }}
    div[data-testid="stFormSubmitButton"] button:hover {{
        color: var(--accent-ink);
        filter: brightness(1.07);
        transform: translateY(-1px);
    }}
    div[data-testid="stMetric"] {{
        background: var(--surface-alt);
        border-left: 2px solid var(--accent);
        padding: .65rem .8rem;
    }}
    div[data-testid="stMetricLabel"] p {{ color: var(--muted) !important; }}
    [data-testid="stProgressBar"] > div {{ background: var(--surface-alt); }}
    [data-testid="stProgressBar"] > div > div {{ background: var(--accent); }}
    hr {{ border-color: var(--line); margin: .75rem 0; }}
    [data-testid="stToggle"] label {{ color: var(--muted); font-size: .75rem; }}

    @media (max-width: 760px) {{
        .block-container {{ padding: .8rem .9rem 1.2rem; }}
        .hero-title {{ font-size: clamp(2.15rem, 11vw, 3.2rem); }}
        .hero-copy {{ font-size: .9rem; }}
        div[data-testid="stForm"] {{ padding: .75rem .75rem .65rem; }}
        .section-note {{ margin-bottom: .4rem; }}
        div[data-testid="stSelectbox"], div[data-testid="stNumberInput"] {{ margin-bottom: -.25rem; }}
        hr {{ margin: .55rem 0; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Load the training artifacts
# -----------------------------------------------------------------------------
@st.cache_resource
def load_artifacts():
    model = joblib.load("churn_model.pkl")
    scaler = joblib.load("scaler.pkl")
    model_columns = joblib.load("model_columns.pkl")
    threshold = float(joblib.load("threshold.pkl"))
    return model, scaler, model_columns, threshold


try:
    model, scaler, model_columns, threshold = load_artifacts()
except FileNotFoundError as exc:
    st.error(f"A required model artifact is missing: {exc.filename}")
    st.info(
        "Keep churn_model.pkl, scaler.pkl, model_columns.pkl, and threshold.pkl "
        "in the same folder as app.py."
    )
    st.stop()


# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
with header_col:
    st.markdown('<div class="eyebrow">Churn / Signal &nbsp;·&nbsp; ML experiment 01</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">Customer retention,<br>measured.</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-copy">A closer look at the signals behind customer churn. '
        'Build a customer profile and see what the model estimates.</p>',
        unsafe_allow_html=True,
    )

st.divider()

metric_one, metric_two, metric_three = st.columns(3)
with metric_one:
    st.markdown('<div class="metric-label">Test ROC-AUC</div><div class="metric-value">0.8408</div>', unsafe_allow_html=True)
with metric_two:
    st.markdown('<div class="metric-label">Recall at 0.30</div><div class="metric-value">74.87%</div>', unsafe_allow_html=True)
with metric_three:
    st.markdown('<div class="metric-label">Model</div><div class="metric-value">Logistic regression</div>', unsafe_allow_html=True)

st.markdown('<div class="small-print">Notebook test-set results. The lower decision threshold favours recall and can produce more false positives.</div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Customer form
# -----------------------------------------------------------------------------
with st.form("customer_profile", border=False):
    profile_col, services_col = st.columns([0.92, 1.08], gap="large")

    with profile_col:
        st.markdown('<div class="section-kicker">01 / Customer & account</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-note">Personal details, contract, and billing profile.</div>', unsafe_allow_html=True)

        gender = st.selectbox("Gender", ["Male", "Female"])
        senior_citizen = st.selectbox("Senior citizen", ["No", "Yes"])
        partner = st.selectbox("Has partner", ["No", "Yes"])
        dependents = st.selectbox("Has dependents", ["No", "Yes"])
        tenure = st.slider("Tenure", min_value=0, max_value=72, value=12, help="Number of months the customer has stayed with the provider.")

        st.divider()
        contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
        payment_method = st.selectbox(
            "Payment method",
            ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
        )
        monthly_charges = st.number_input("Monthly charges ($)", min_value=0.0, max_value=200.0, value=70.0, step=1.0)
        total_charges = st.number_input("Total charges ($)", min_value=0.0, max_value=10000.0, value=840.0, step=10.0)

    with services_col:
        st.markdown('<div class="section-kicker">02 / Services subscribed</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-note">Choose the services currently attached to this account.</div>', unsafe_allow_html=True)

        service_left, service_right = st.columns(2, gap="medium")
        with service_left:
            phone_service = st.selectbox("Phone service", ["No", "Yes"])
            multiple_lines = st.selectbox("Multiple lines", ["No", "Yes", "No phone service"])
            internet_service = st.selectbox("Internet service", ["DSL", "Fiber optic", "No"])
            online_security = st.selectbox("Online security", ["No", "Yes", "No internet service"])
        with service_right:
            paperless_billing = st.selectbox("Paperless billing", ["No", "Yes"])
            online_backup = st.selectbox("Online backup", ["No", "Yes", "No internet service"])
            device_protection = st.selectbox("Device protection", ["No", "Yes", "No internet service"])
            tech_support = st.selectbox("Tech support", ["No", "Yes", "No internet service"])

        stream_left, stream_right = st.columns(2, gap="medium")
        with stream_left:
            streaming_tv = st.selectbox("Streaming TV", ["No", "Yes", "No internet service"])
        with stream_right:
            streaming_movies = st.selectbox("Streaming movies", ["No", "Yes", "No internet service"])

    st.write("")
    submitted = st.form_submit_button("Calculate churn risk", use_container_width=True)


# -----------------------------------------------------------------------------
# Preprocess and predict using the same feature layout as training
# -----------------------------------------------------------------------------
if submitted:
    raw_input = {
        "gender": 1 if gender == "Male" else 0,
        "SeniorCitizen": 1 if senior_citizen == "Yes" else 0,
        "Partner": 1 if partner == "Yes" else 0,
        "Dependents": 1 if dependents == "Yes" else 0,
        "tenure": tenure,
        "PhoneService": 1 if phone_service == "Yes" else 0,
        "PaperlessBilling": 1 if paperless_billing == "Yes" else 0,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges,
        "MultipleLines": multiple_lines,
        "InternetService": internet_service,
        "OnlineSecurity": online_security,
        "OnlineBackup": online_backup,
        "DeviceProtection": device_protection,
        "TechSupport": tech_support,
        "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies,
        "Contract": contract,
        "PaymentMethod": payment_method,
    }

    input_df = pd.DataFrame([raw_input])
    categorical_columns = [
        "MultipleLines", "InternetService", "OnlineSecurity", "OnlineBackup",
        "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies",
        "Contract", "PaymentMethod",
    ]
    input_encoded = pd.get_dummies(input_df, columns=categorical_columns)
    input_aligned = input_encoded.reindex(columns=model_columns, fill_value=0)
    input_scaled = scaler.transform(input_aligned)

    churn_probability = float(model.predict_proba(input_scaled)[0, 1])
    is_higher_risk = churn_probability >= threshold

    st.divider()
    st.markdown('<div class="section-kicker">03 / Prediction</div>', unsafe_allow_html=True)
    result_left, result_right = st.columns([1.15, 1], gap="large", vertical_alignment="center")

    with result_left:
        if is_higher_risk:
            st.error("Higher churn risk")
            st.markdown(
                '<div class="result-copy">This profile is above the model’s decision cut-off. '
                'A retention conversation or a review of the customer’s current plan may be worth considering.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.success("Lower churn risk")
            st.markdown(
                '<div class="result-copy">This profile is below the model’s decision cut-off. '
                'The prediction does not guarantee that the customer will stay.</div>',
                unsafe_allow_html=True,
            )

    with result_right:
        st.metric("Estimated churn probability", f"{churn_probability:.1%}")
        st.progress(churn_probability)
        st.caption(f"Classification cut-off: {threshold:.0%}")

    st.markdown(
        '<p class="small-print">This is a model estimate based on the supplied attributes, not a certainty or '
        'a substitute for business context. The lower cut-off is intended to catch more potential churners, '
        'which also means some customers may be flagged incorrectly.</p>',
        unsafe_allow_html=True,
    )
else:
    st.caption("Complete the customer profile and select **Calculate churn risk** to see the prediction.")
