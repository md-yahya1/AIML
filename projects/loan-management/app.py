import json
import os
import subprocess
from typing import Any, Dict

import pandas as pd
import streamlit as st
from loan_model import load_model, load_data, train_and_save

MODEL_PATH = "model_pipeline.joblib"
FEATURE_INFO = "feature_info.json"
DEFAULT_CSV = "loan_approval_data.csv"


def train_from_csv(csv_path: str = DEFAULT_CSV):
    with st.spinner("Training model — this may take a moment..."):
        train_and_save(csv_path, MODEL_PATH, FEATURE_INFO)
    st.success("Training complete and model saved.")


def main():
    st.title("Loan Approval Demo — Streamlit")
    st.markdown("Simple demo to train and predict loan approvals.")

    uploaded = st.file_uploader("Upload CSV (optional)", type=["csv"])
    csv_path = DEFAULT_CSV
    if uploaded is not None:
        df = pd.read_csv(uploaded)
        st.write("Dataset preview:")
        st.dataframe(df.head())
        if st.button("Train model on uploaded CSV"):
            df.to_csv("uploaded_data.csv", index=False)
            train_from_csv("uploaded_data.csv")
            csv_path = "uploaded_data.csv"
    else:
        if os.path.exists(DEFAULT_CSV):
            if st.button("Train model on existing CSV"):
                train_from_csv(DEFAULT_CSV)
        else:
            st.info("No CSV found in workspace. Upload a CSV or add loan_approval_data.csv to workspace.")

    model_exists = os.path.exists(MODEL_PATH) and os.path.exists(FEATURE_INFO)
    if model_exists:
        st.success("Model is available — you can make predictions below.")
        with open(FEATURE_INFO, "r", encoding="utf-8") as f:
            info: Dict[str, Any] = json.load(f)

        st.subheader("Make a single prediction")
        sample_input = {}
        for c in info.get("numeric_cols", []):
            default = info.get("numeric_defaults", {}).get(c, 0.0)
            sample_input[c] = st.number_input(c, value=float(default))

        # For categorical columns, prefer showing a selectbox of observed values
        for c in info.get("categorical_cols", []):
            options = None
            # if user uploaded a file, use its values
            if uploaded is not None and c in df.columns:
                options = df[c].dropna().unique().tolist()
            else:
                # try to read values from the default CSV in workspace
                if os.path.exists(DEFAULT_CSV):
                    try:
                        tmp = pd.read_csv(DEFAULT_CSV)
                        if c in tmp.columns:
                            options = tmp[c].dropna().unique().tolist()
                    except Exception:
                        options = None

            if options and len(options) > 0:
                # limit very large lists
                if len(options) > 200:
                    sample_input[c] = st.text_input(c, value="")
                else:
                    sample_input[c] = st.selectbox(c, options)
            else:
                sample_input[c] = st.text_input(c, value="")

        if st.button("Predict"):
            input_df = pd.DataFrame([sample_input])
            model = load_model(MODEL_PATH)
            proba = model.predict_proba(input_df)[0]
            pred = model.predict(input_df)[0]
            # display prediction safely whether it's numeric or string
            try:
                display_pred = int(pred)
            except Exception:
                display_pred = pred
            st.write("Prediction:", display_pred)
            # show model classes and probabilities for clarity
            try:
                classes = model.classes_.tolist()
                st.write("Model classes:", classes)
            except Exception:
                pass
            st.write("Probabilities:", proba.tolist())

        st.subheader("Batch predict from CSV")
        if st.button("Predict on workspace CSV"):
            df = pd.read_csv(csv_path)
            model = load_model(MODEL_PATH)
            X = df[info["columns"]]
            preds = model.predict(X)
            df_result = df.copy()
            df_result["predicted_loan_approved"] = preds
            st.dataframe(df_result.head())
            out_path = "predictions.csv"
            df_result.to_csv(out_path, index=False)
            st.success(f"Saved predictions to {out_path}")
    else:
        st.warning("No trained model found. Train a model first.")

    st.sidebar.markdown("## Actions")
    if st.sidebar.button("Retrain model from default CSV"):
        if os.path.exists(DEFAULT_CSV):
            train_from_csv(DEFAULT_CSV)
        else:
            st.warning("Default CSV not found in workspace")

    st.sidebar.markdown("---")
    st.sidebar.write("Files created: model_pipeline.joblib, feature_info.json")


if __name__ == "__main__":
    main()
