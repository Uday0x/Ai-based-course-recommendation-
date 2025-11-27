"""
Train a loan eligibility classifier on synthetic data and save artifacts.

Usage:
    python scripts/train_model.py --output-dir models --seed 42 --n-samples 20000

Outputs:
- models/model.joblib
- models/scaler.joblib
- models/vectorizer.joblib
- models/meta.json
- models/test_data.csv
- backend/data/sample_loans.csv
"""
import argparse
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import joblib
import os
import json

LOAN_PURPOSES = ["debt_consolidation", "home_improvement", "small_business", "car", "other"]

def generate_synthetic(n=10000, seed=42):
    rng = np.random.RandomState(seed)
    income = rng.normal(60000, 25000, size=n).clip(8000, 300000)
    employment_length = rng.exponential(5, size=n).clip(0, 40)
    credit_score = rng.normal(680, 60, size=n).clip(300, 850)
    debt_to_income = rng.beta(2, 5, size=n)  # 0..1
    loan_amount = rng.normal(15000, 10000, size=n).clip(1000, 100000)
    loan_purpose = rng.choice(LOAN_PURPOSES, size=n, p=[0.4,0.15,0.1,0.15,0.2])
    age = rng.normal(40, 12, size=n).clip(18, 90).astype(int)
    # sensitive attribute (simulate gender) for fairness checks
    gender = rng.choice(["male","female"], size=n, p=[0.53,0.47])
    # scoring heuristic
    score = (
        (credit_score - 600) / 100.0
        + (income / 50000.0)
        - debt_to_income * 2.5
        + np.where(loan_purpose == "small_business", -0.5, 0.0)
        - (loan_amount / (income + 1)) * 0.3
        + (employment_length / 10.0)
    )
    # introduce bias effect for demonstration (do NOT introduce in real systems)
    score += np.where(gender == "male", 0.05, -0.05)
    prob = 1 / (1 + np.exp(-score))
    approved = (rng.rand(n) < prob).astype(int)
    df = pd.DataFrame({
        "income": income,
        "employment_length": employment_length,
        "credit_score": credit_score,
        "debt_to_income": debt_to_income,
        "loan_amount": loan_amount,
        "loan_purpose": loan_purpose,
        "age": age,
        "gender": gender,
        "approved": approved
    })
    return df

def build_features(df):
    # numeric features
    num_cols = ["income","employment_length","credit_score","debt_to_income","loan_amount","age"]
    X_num = df[num_cols].values
    # vectorize categorical fields
    dv = DictVectorizer(sparse=False)
    cat = df[["loan_purpose"]].to_dict(orient="records")
    X_cat = dv.fit_transform(cat)
    X = np.hstack([X_num, X_cat])
    feature_names = num_cols + list(dv.get_feature_names_out())
    return X, df["approved"].values, dv, feature_names

def compute_fairness_metrics(df, preds, probs, sensitive_col="gender"):
    out = {}
    groups = df[sensitive_col].unique().tolist()
    for g in groups:
        mask = df[sensitive_col] == g
        grp_preds = preds[mask]
        grp_probs = probs[mask]
        grp_actual = df.loc[mask, "approved"].values
        tpr = ((grp_preds == 1) & (grp_actual == 1)).sum() / max(1, (grp_actual == 1).sum())
        fpr = ((grp_preds == 1) & (grp_actual == 0)).sum() / max(1, (grp_actual == 0).sum())
        approval_rate = (grp_preds == 1).mean()
        out[g] = {"tpr": float(round(tpr, 3)), "fpr": float(round(fpr, 3)), "approval_rate": float(round(approval_rate, 3))}
    return out

def main(output_dir="models", seed=42, n_samples=10000):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(output_dir), "data"), exist_ok=True)
    df = generate_synthetic(n=n_samples, seed=seed)
    X, y, dv, feature_names = build_features(df)
    # scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    # split
    X_train, X_test, y_train, y_test, df_train, df_test = train_test_split(
        X_scaled, y, df, test_size=0.2, random_state=seed, stratify=y
    )
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:,1]
    auc = roc_auc_score(y_test, probs)
    report = classification_report(y_test, preds, output_dict=True)
    print("AUC:", auc)
    print("Classification report:")
    print(classification_report(y_test, preds))
    # fairness metrics on test set
    df_test = df_test.copy()
    df_test["pred"] = preds
    df_test["prob"] = probs
    fairness = compute_fairness_metrics(df_test, preds, probs, sensitive_col="gender")
    # save artifacts
    joblib.dump(model, os.path.join(output_dir, "model.joblib"))
    joblib.dump(scaler, os.path.join(output_dir, "scaler.joblib"))
    joblib.dump(dv, os.path.join(output_dir, "vectorizer.joblib"))
    meta = {
        "feature_names": feature_names,
        "metrics": {"auc": float(round(auc, 4)), "report": report},
        "fairness": fairness,
        "generated_samples": n_samples,
        "note": "Synthetic dataset for demo purposes only."
    }
    with open(os.path.join(output_dir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    df_test.to_csv(os.path.join(output_dir, "test_data.csv"), index=False)
    # write a small sample to backend/data
    df.sample(20, random_state=seed).to_csv(os.path.join(os.path.dirname(output_dir), "data/sample_loans.csv"), index=False)
    print(f"Saved model and artifacts to {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="models")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-samples", type=int, default=20000)
    args = parser.parse_args()
    main(output_dir=args.output_dir, seed=args.seed, n_samples=args.n_samples)