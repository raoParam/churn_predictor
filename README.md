# Customer Churn Prediction

A machine learning project that estimates whether a telecom customer may leave their service. The Streamlit app accepts a customer profile and returns an estimated churn probability with a higher- or lower-risk classification.

**Live app:** https://churn-predictore.streamlit.app/  
**GitHub repository:** https://github.com/raoParam/churn_predictor

## What it does

- Collects customer, account, service, contract, and billing details.
- Applies the same feature encoding, column alignment, and scaling used during model training.
- Estimates the probability of churn.
- Uses a saved classification threshold of **0.30** to flag higher-risk profiles.

The threshold was lowered from the default 0.50 to prioritize recall. This helps identify more customers who actually churn, but it also increases false positives. This is a learning project and should not be treated as a production retention or decision system.

## Model development

The project uses the [IBM Telco Customer Churn dataset](https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv) and follows this workflow in the notebook:

1. Inspect and clean the data, including converting `TotalCharges` to numeric and filling the small number of missing values.
2. Encode binary and multi-category features.
3. Split the data into training and test sets using a stratified 80/20 split.
4. Scale features and explore feature selection and PCA.
5. Compare Logistic Regression, K-Nearest Neighbors, and Random Forest.
6. Tune Logistic Regression, Random Forest, and Gradient Boosting with 5-fold stratified cross-validation, optimizing ROC-AUC.
7. Compare the tuned models on the held-out test set.
8. Lower the Logistic Regression decision threshold to 0.30 to prioritize recall.
9. Save the model and preprocessing artifacts for the Streamlit app.

## Evaluation

The notebook's final tuned-model comparison reports the following held-out test results using the default **0.50 classification threshold**:

| Model | Accuracy | Recall | Precision | ROC-AUC |
|---|---:|---:|---:|---:|
| Logistic Regression (tuned) | **80.13%** | 55.08% | 64.78% | **0.8408** |
| Random Forest (tuned) | 78.99% | 39.84% | 67.73% | 0.8444 |
| Gradient Boosting (tuned) | 79.84% | 50.80% | 65.52% | 0.8417 |

Logistic Regression was selected for the app. The notebook then evaluated it at the app's **0.30 threshold**:

| Metric | Threshold 0.50 | Threshold 0.30 |
|---|---:|---:|
| Accuracy | 80.13% | 74.80% |
| Recall | 55.08% | **74.87%** |
| Precision | **64.78%** | 51.76% |

ROC-AUC is calculated from predicted probabilities and does not depend on the chosen classification threshold. Accuracy, recall, and precision do depend on that threshold. The figures above are from the notebook's recorded test-set outputs; performance on new data may differ.

## Tech stack

- Python
- Pandas and NumPy
- Scikit-learn
- Streamlit
- Joblib
- Jupyter Notebook

## Run locally

1. Clone this repository:

   ```bash
   git clone https://github.com/raoParam/churn_predictor.git
   cd churn_predictor
   ```

2. Create and activate a virtual environment (recommended).

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the Streamlit app:

   ```bash
   streamlit run app.py
   ```

## Project structure

```text
churn_predictor/
├── app.py
├── churn_model.pkl
├── model_columns.pkl
├── scaler.pkl
├── threshold.pkl
├── requirements.txt
└── README.md
```

The `.pkl` files are generated from the notebook and are required by the app:

- `churn_model.pkl` — tuned Logistic Regression search object.
- `scaler.pkl` — fitted feature scaler.
- `model_columns.pkl` — expected feature names and order after encoding and feature selection.
- `threshold.pkl` — saved decision threshold (`0.30`).

## What I learned

This project gave me practice with data cleaning, categorical encoding, stratified train-test splitting, feature scaling, model comparison, feature selection, PCA, cross-validation, hyperparameter tuning, evaluation metrics, threshold selection, and deploying a model with Streamlit.

---

Built as a machine learning learning project.
