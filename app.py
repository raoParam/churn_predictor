import streamlit as st
import pandas as pd
import numpy as np
import joblib

# ============================================
# Load saved artifacts
# ============================================
# TODO 1: Load the 4 files we saved (model, scaler, column list, threshold)
model = joblib.load('churn_model.pkl')
scaler = joblib.load('scaler.pkl')
model_columns = joblib.load('model_columns.pkl')
threshold = joblib.load('threshold.pkl')

st.set_page_config(page_title="Customer Churn Predictor", page_icon="📉", layout="centered")
st.title("Customer Churn Prediction")
st.markdown("Enter customer details to predict churn risk.")

# ============================================
# Collect user input (this part is given — pure UI, no ML logic)
# ============================================
col1, col2 = st.columns(2)

with col1:
    gender = st.selectbox("Gender", ["Male", "Female"])
    senior_citizen = st.selectbox("Senior Citizen", ["No", "Yes"])
    partner = st.selectbox("Has Partner", ["No", "Yes"])
    dependents = st.selectbox("Has Dependents", ["No", "Yes"])
    tenure = st.slider("Tenure (months)", 0, 72, 12)
    phone_service = st.selectbox("Phone Service", ["No", "Yes"])
    paperless_billing = st.selectbox("Paperless Billing", ["No", "Yes"])
    contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])

with col2:
    multiple_lines = st.selectbox("Multiple Lines", ["No", "Yes", "No phone service"])
    internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
    online_security = st.selectbox("Online Security", ["No", "Yes", "No internet service"])
    online_backup = st.selectbox("Online Backup", ["No", "Yes", "No internet service"])
    device_protection = st.selectbox("Device Protection", ["No", "Yes", "No internet service"])
    tech_support = st.selectbox("Tech Support", ["No", "Yes", "No internet service"])
    streaming_tv = st.selectbox("Streaming TV", ["No", "Yes", "No internet service"])
    streaming_movies = st.selectbox("Streaming Movies", ["No", "Yes", "No internet service"])

payment_method = st.selectbox("Payment Method", 
    ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"])
monthly_charges = st.number_input("Monthly Charges ($)", min_value=0.0, max_value=200.0, value=70.0)
total_charges = st.number_input("Total Charges ($)", min_value=0.0, max_value=10000.0, value=840.0)

# ============================================
# Build the raw input dataframe (mirrors the ORIGINAL df structure before encoding)
# ============================================
if st.button("Predict Churn"):

    # TODO 2: Build a single-row dict matching the ORIGINAL raw column names
    # (same names/values as your df BEFORE encoding — LabelEncoder used 0/1, get_dummies used raw category text)
    raw_input = {
        'gender': 1 if gender == "Male" else 0,   # matches how LabelEncoder encoded it during training
        'SeniorCitizen': 1 if senior_citizen == "Yes" else 0,
        'Partner': 1 if partner == "Yes" else 0,   # same pattern as gender/SeniorCitizen above
        'Dependents': 1 if dependents == "Yes" else 0,
        'tenure': tenure,
        'PhoneService': 1 if phone_service == "Yes" else 0,
        'PaperlessBilling': 1 if paperless_billing == "Yes" else 0,
        'MonthlyCharges': monthly_charges,
        'TotalCharges': total_charges,
        'MultipleLines': multiple_lines,             # raw text — will be one-hot encoded below
        'InternetService': internet_service,
        'OnlineSecurity': online_security,
        'OnlineBackup': online_backup,
        'DeviceProtection': device_protection,
        'TechSupport': tech_support,
        'StreamingTV': streaming_tv,
        'StreamingMovies': streaming_movies,
        'Contract': contract,
        'PaymentMethod': payment_method
    }

    input_df = pd.DataFrame([raw_input])

    # TODO 3: One-hot encode the same multi-category columns we encoded during training
    multi_cat_cols = ['MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup',
                       'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies',
                       'Contract', 'PaymentMethod']

    input_encoded = pd.get_dummies(input_df, columns=multi_cat_cols)

    # TODO 4: THE CRITICAL STEP — align columns to match training exactly
    # Any column the model expects but this row doesn't have gets filled with 0
    # Any extra column not seen during training gets dropped
    input_final = input_encoded.reindex(columns=model_columns, fill_value=0)

    # TODO 5: Scale using the SAME fitted scaler from training (never re-fit here!)
    input_scaled = scaler.transform(input_final)

    # TODO 6: Predict probability of churn (class 1)
    churn_proba = model.predict_proba(input_scaled)[:, 1][0]

    # TODO 7: Apply our chosen threshold (0.3, not sklearn's default 0.5)
    prediction = 1 if churn_proba >= threshold else 0

    # ============================================
    # Display results (given — pure UI)
    # ============================================
    st.divider()
    if prediction == 1:
        st.error(f"⚠️ High Churn Risk — Probability: {churn_proba:.1%}")
        st.write("**Recommendation:** Consider proactive retention offer (discount, contract upgrade incentive).")
    else:
        st.success(f"✅ Low Churn Risk — Probability: {churn_proba:.1%}")

    st.progress(min(float(churn_proba), 1.0))
    st.caption(f"Decision threshold: {threshold} (tuned for higher recall — catches more true churners)")