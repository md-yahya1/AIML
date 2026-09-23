# Loan Approval — Streamlit Demo

Lightweight demo to train and serve a loan-approval classifier with Streamlit.

Key files
- `loan_model.py` — build/train/save a sklearn pipeline (`model_pipeline.joblib`) and feature info.
- `train.py` — minimal CLI to train from a CSV (expects `Loan_Approved` target).
- `app.py` — Streamlit UI to train (workspace or uploaded CSV) and make single/batch predictions.
- `requirements.txt` — Python dependencies.

Quick start

1. Create and activate a virtualenv (Windows):

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install deps:

```bash
pip install -r requirements.txt
```

3. Train the model (uses `loan_approval_data.csv` by default):

```bash
python train.py "loan_approval_data.csv"
```

4. Launch the app:

```bash
streamlit run app.py
```

Notes
- The trainer drops rows with a missing `Loan_Approved` value before fitting.
- The app shows select boxes for categorical fields when values are available in the uploaded or workspace CSV.
