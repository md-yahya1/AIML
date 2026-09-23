import json
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer


def load_data(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def _prepare_feature_info(df: pd.DataFrame, target_col: str):
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in dataframe")
    X = df.drop(columns=[target_col])
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = X.select_dtypes(include=[object, "category"]).columns.tolist()
    numeric_defaults = {c: float(X[c].median()) if not X[c].isnull().all() else 0.0 for c in numeric_cols}

    return {
        "columns": X.columns.tolist(),
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "numeric_defaults": numeric_defaults,
    }


def build_pipeline(numeric_cols, categorical_cols):
    num_pipeline = Pipeline([("imputer", SimpleImputer(strategy="mean")), ("scaler", StandardScaler())])
    cat_pipeline = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])

    preprocessor = ColumnTransformer([("num", num_pipeline, numeric_cols), ("cat", cat_pipeline, categorical_cols)], remainder="drop")
    pipeline = Pipeline([("preprocessor", preprocessor), ("clf", GaussianNB())])
    return pipeline


def train_and_save(csv_path: str, model_path: str = "model_pipeline.joblib", feature_info_path: str = "feature_info.json", target_col: str = "Loan_Approved"):
    df = load_data(csv_path)
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in data")
    # remove rows with missing target
    df = df[df[target_col].notnull()].reset_index(drop=True)

    info = _prepare_feature_info(df, target_col)
    X = df[info["columns"]]
    y = df[target_col]

    pipeline = build_pipeline(info["numeric_cols"], info["categorical_cols"])
    pipeline.fit(X, y)

    joblib.dump(pipeline, model_path)
    with open(feature_info_path, "w", encoding="utf-8") as f:
        json.dump(info, f)

    return model_path, feature_info_path


def load_model(model_path: str = "model_pipeline.joblib"):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    return joblib.load(model_path)


def predict_from_df(df: pd.DataFrame, model_path: str = "model_pipeline.joblib"):
    model = load_model(model_path)
    probs = model.predict_proba(df)
    preds = model.predict(df)
    return {"predictions": preds.tolist(), "probabilities": probs.tolist()}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("csv")
    args = parser.parse_args()
    model_file, feat_file = train_and_save(args.csv)
    print("Saved model to", model_file)
    print("Saved feature info to", feat_file)
