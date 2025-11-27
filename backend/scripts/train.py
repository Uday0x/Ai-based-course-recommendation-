"""
Train a course recommender classifier on synthetic interest lists.

Usage:
    python scripts/train.py --output models --n-samples 5000 --seed 42
"""
import argparse
import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

COURSES = [
    "intro_ml",
    "deep_learning",
    "nlp",
    "computer_vision",
    "data_engineering",
    "ai_ethics",
    "reinforcement_learning"
]

TOPICS = [
    "linear algebra", "probability", "statistics", "python", "pandas", "numpy", "ml",
    "deep learning", "neural networks", "cnn", "rnn", "transformers", "nlp", "cv",
    "computer vision", "data engineering", "etl", "big data", "spark", "hadoop",
    "ethics", "fairness", "explainability", "reinforcement", "rl", "optimization",
    "deploy", "mlo ps", "docker", "tensorflow", "pytorch"
]

# mapping heuristic: which topics strongly indicate which course
COURSE_KEYWORDS = {
    "intro_ml": ["python", "pandas", "numpy", "statistics", "linear algebra", "ml"],
    "deep_learning": ["deep learning", "neural networks", "tensorflow", "pytorch"],
    "nlp": ["nlp", "transformers", "rnn", "sequence", "text"],
    "computer_vision": ["computer vision", "cv", "cnn", "image"],
    "data_engineering": ["data engineering", "etl", "big data", "spark", "hadoop"],
    "ai_ethics": ["ethics", "fairness", "explainability"],
    "reinforcement_learning": ["reinforcement", "rl", "optimization"]
}

def generate_synthetic(n=5000, seed=42):
    rng = np.random.RandomState(seed)
    rows = []
    for _ in range(n):
        # choose 2..6 topics per user
        k = rng.randint(2, 7)
        topics = list(rng.choice(TOPICS, size=k, replace=False))
        # determine label by heuristic: which course has most matching keywords
        scores = {c: 0 for c in COURSES}
        for c, keys in COURSE_KEYWORDS.items():
            for t in topics:
                for key in keys:
                    if key in t:
                        scores[c] += 1
        # add some noise
        if all(v == 0 for v in scores.values()):
            label = rng.choice(COURSES)
        else:
            # pick max, with small probability to pick a different one to simulate noise
            if rng.rand() < 0.15:
                label = rng.choice(COURSES)
            else:
                label = max(scores.items(), key=lambda x: x[1])[0]
        rows.append({"interests": ", ".join(topics), "label": label})
    return pd.DataFrame(rows)

def main(output="models", n_samples=5000, seed=42, model_type="rf"):
    os.makedirs(output, exist_ok=True)
    df = generate_synthetic(n=n_samples, seed=seed)
    X_raw = df["interests"].values
    y = df["label"].values
    vect = CountVectorizer(token_pattern=r"(?u)\b[\w\s]+\b")
    X = vect.fit_transform(X_raw)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=seed, stratify=y)
    if model_type == "rf":
        model = RandomForestClassifier(n_estimators=200, random_state=seed)
    else:
        model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)
    acc = accuracy_score(y_test, preds)
    print("Accuracy on test:", acc)
    print(classification_report(y_test, preds))
    # Save artifacts
    joblib.dump(model, os.path.join(output, "model.joblib"))
    joblib.dump(vect, os.path.join(output, "vectorizer.joblib"))
    meta = {"classes": list(model.classes_), "vectorizer_vocab_size": len(vect.get_feature_names_out())}
    with open(os.path.join(output, "meta.json"), "w") as f:
        json.dump(meta, f)
    # save a small sample
    df.sample(20, random_state=seed).to_csv(os.path.join(os.path.dirname(output), "data", "sample_interests.csv"), index=False)
    print(f"Saved model and vectorizer to {output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="models")
    parser.add_argument("--n-samples", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--model-type", choices=["rf", "logreg"], default="rf")
    args = parser.parse_args()
    main(output=args.output, n_samples=args.n_samples, seed=args.seed, model_type=args.model_type)