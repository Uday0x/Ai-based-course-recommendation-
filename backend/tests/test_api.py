from fastapi.testclient import TestClient
import os, sys, json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app
import joblib
import tempfile

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_predict_with_dummy_model(monkeypatch, tmp_path):
    # create a tiny trained model artifacts so load_artifacts can succeed
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.linear_model import LogisticRegression
    import numpy as np
    vect = CountVectorizer(token_pattern=r"(?u)\b[\w\s]+\b")
    docs = ["python ml", "deep learning neural networks", "nlp transformers", "computer vision cnn"]
    X = vect.fit_transform(docs)
    y = np.array(["intro_ml", "deep_learning", "nlp", "computer_vision"])
    model = LogisticRegression(max_iter=1000, multi_class="ovr")
    model.fit(X, y)
    model_path = tmp_path / "model.joblib"
    vect_path = tmp_path / "vectorizer.joblib"
    meta_path = tmp_path / "meta.json"
    joblib.dump(model, str(model_path))
    joblib.dump(vect, str(vect_path))
    with open(meta_path, "w") as f:
        json.dump({"classes": list(model.classes_)}, f)
    monkeypatch.setenv("MODEL_DIR", str(tmp_path))
    # reload artifacts
    from app import model as m
    m._model = None
    m._vectorizer = None
    m._meta = {}
    m.load_artifacts()
    payload = {"interests": "python, numpy"}
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert "recommended_course" in body
    assert "probability" in body
    assert "explanation" in body