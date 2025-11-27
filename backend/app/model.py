import os
import joblib
import json
import numpy as np
from typing import Tuple, Dict, Any
from sklearn.feature_extraction.text import CountVectorizer

MODEL_DIR = os.environ.get("MODEL_DIR", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "model.joblib")
VECT_PATH = os.path.join(MODEL_DIR, "vectorizer.joblib")
META_PATH = os.path.join(MODEL_DIR, "meta.json")

_model = None
_vectorizer = None
_meta = {}

def load_artifacts():
    global _model, _vectorizer, _meta
    if _model is None:
        if os.path.exists(MODEL_PATH):
            _model = joblib.load(MODEL_PATH)
    if _vectorizer is None:
        if os.path.exists(VECT_PATH):
            _vectorizer = joblib.load(VECT_PATH)
    if os.path.exists(META_PATH):
        with open(META_PATH, "r") as f:
            _meta = json.load(f)

def _normalize_interests(text: str) -> str:
    # basic normalization: lowercase, remove duplicates, strip
    toks = [t.strip().lower() for t in text.split(",") if t.strip()]
    # collapse multi-word tokens (keep spaces) but strip extra whitespace
    unique = list(dict.fromkeys(toks))
    return " ".join(unique)

def predict_from_interests(interests_text: str) -> Tuple[str, float, Dict[str, Any]]:
    global _model, _vectorizer, _meta
    if _model is None or _vectorizer is None:
        raise RuntimeError("Model artifacts not loaded. Run training script to generate models.")

    # Normalize input to a predictable form (space-separated tokens)
    norm = _normalize_interests(interests_text)

    # Try transforming as text first (CountVectorizer case).
    # If that fails (e.g. DictVectorizer expects dicts), build a token->count dict and retry.
    X = None
    try:
        X = _vectorizer.transform([norm])
    except Exception as e:
        # fallback: vectorizer probably expects mapping-like inputs (DictVectorizer)
        try:
            # build token->count dict from normalized string
            tokens = [t.strip() for t in norm.split() if t.strip()]
            feature_dict = {}
            for t in tokens:
                feature_dict[t] = feature_dict.get(t, 0) + 1
            # try again with dict (list-of-dicts)
            X = _vectorizer.transform([feature_dict])
        except Exception as e2:
            # both attempts failed — raise original error with context
            raise RuntimeError(f"Vectorizer transform failed for both text and dict forms. "
                               f"First error: {e!r}; Fallback error: {e2!r}")

    # Proceed with prediction as before
    try:
        probs = _model.predict_proba(X)[0]
    except Exception as e:
        raise RuntimeError(f"Model predict_proba failed: {e}")

    # pick predicted class
    idx = int(np.argmax(probs))
    course = _meta.get("classes", [])[idx] if _meta.get("classes") else str(idx)
    prob = float(probs[idx])

    # build explanation (same logic as before)
    explanation = {}
    try:
        if hasattr(_model, "feature_importances_"):
            importances = _model.feature_importances_
            tokens = _vectorizer.get_feature_names_out()
            present = X.toarray()[0]
            contribs = {}
            for tok, pres, imp in zip(tokens, present, importances):
                if pres:
                    contribs[tok] = float(imp)
            top = dict(sorted(contribs.items(), key=lambda x: x[1], reverse=True)[:5])
            explanation = {"method": "feature_importances", "top_contributing_tokens": top}
        elif hasattr(_model, "coef_"):
            tokens = _vectorizer.get_feature_names_out()
            coefs = _model.coef_[idx]
            present = X.toarray()[0]
            contribs = {}
            for tok, pres, c in zip(tokens, present, coefs):
                if pres:
                    contribs[tok] = float(c * pres)
            top = dict(sorted(contribs.items(), key=lambda x: abs(x[1]), reverse=True)[:5])
            explanation = {"method": "coef_contributions", "top_contributing_tokens": top}
        else:
            explanation = {"method": "none", "note": "No explanation available for this model type."}
    except Exception:
        explanation = {"method": "error", "note": "Failed to produce explanation."}

    return course, prob, explanation




# backend/debug_artifacts.py
import json, os
from app import model as M

print("MODEL_PATH:", os.path.abspath(M.MODEL_PATH))
print("VECT_PATH:", os.path.abspath(M.VECT_PATH))
print("META_PATH:", os.path.abspath(M.META_PATH))

print("_model type:", type(M._model))
print("_vectorizer type:", type(M._vectorizer))
print("_meta keys:", list(M._meta.keys()))

# feature info
try:
    feat_names = M._vectorizer.get_feature_names_out()
    print("vectorizer feature count:", len(feat_names))
    print("vectorizer features:", list(feat_names))
except Exception as e:
    print("vectorizer.get_feature_names_out() error:", e)
    try:
        print("vectorizer.vocabulary_.size:", len(getattr(M._vectorizer, "vocabulary_", {})))
    except Exception:
        pass

# model coef info
try:
    if hasattr(M._model, "coef_"):
        print("model.coef_.shape:", M._model.coef_.shape)
    if hasattr(M._model, "classes_"):
        print("model.classes_:", list(M._model.classes_))
    print("model type repr:", repr(M._model))
except Exception as e:
    print("model info error:", e)

# Look for stored feature names in meta
print("meta content (first 200 chars):", json.dumps(M._meta)[:200])
