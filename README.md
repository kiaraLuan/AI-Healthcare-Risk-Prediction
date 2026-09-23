# AI-Based Chronic and Mental Healthcare Risk Prediction — MVP

## What This Is
A minimum viable product demonstrating AI-based risk prediction for
chronic disease (diabetes) and mental health (stress/anxiety/depression),
using publicly available structured datasets. Built as a proof of concept
for early risk awareness — not a diagnostic tool.

## How to Run
1. Clone the repo
2. Create a virtual environment: `python -m venv venv`
3. Activate it and install dependencies: `pip install -r requirements.txt`
4. Run the app: `streamlit run frontend/app.py`

## What's Included (MVP Scope)
- Chronic health risk assessment (8 input features, Random Forest model)
- Mental health risk assessment (DASS-21 questionnaire, Random Forest model)
- Risk category + confidence score for both modules
- Basic two-point history comparison (improving / stable / increasing)
- SQLite storage of past assessments

## What's Deferred (Full Project Scope)
- Comparison across 6 ML/DL algorithms (Logistic Regression, Decision Tree,
  SVM, XGBoost, Neural Network)
- SHAP-based explainability
- Full trend dashboard with visualizations
- Separate backend API (current MVP runs model inference directly in Streamlit)

## Datasets Used
- CDC Diabetes Health Indicators (UCI ML Repository, ID 891)
- Mental Health Dataset based on DASS-21 (Mendeley Data, DOI 10.17632/br82d4xkj7.1)

## Project Structure
/data          - raw and processed datasets
/notebooks     - EDA and model training notebooks
/models        - saved trained models (.pkl)
/frontend      - Streamlit application
/docs          - synopsis, backlog, feature spec

## Known Limitations
- Trained on public datasets, not clinical data
- Not validated for real-world medical use
- MVP scope only — see "What's Deferred" above

## Author
Kiara Fernandes — Final Year Computer Engineering, PCCE