# create_course_artifacts.py
import json, os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# tiny example dataset (course descriptions)
docs = [
    "introduction to python programming and data structures",
    "machine learning with python, numpy, pandas",
    "deep learning with tensorflow and pytorch, nlp",
    "frontend web development with react and javascript",
    "backend development with node express and databases",
    "mobile app development with flutter and dart",
    "cloud computing and devops automation kubernetes",
    "database design and sql performance optimization",
]
labels = [
    "Python Basics",
    "Machine Learning",
    "Deep Learning",
    "Frontend Development",
    "Backend Development",
    "Mobile Development",
    "Cloud & DevOps",
    "Databases"
]

# train vectorizer + simple classifier
vect = CountVectorizer()
X = vect.fit_transform(docs)
clf = LogisticRegression(max_iter=1000)
clf.fit(X, labels)

# save artifacts
joblib.dump(clf, os.path.join(MODEL_DIR, "model.joblib"))
joblib.dump(vect, os.path.join(MODEL_DIR, "vectorizer.joblib"))

meta = {"classes": list(clf.classes_), "note": "small demo course recommender (dev only)"}
with open(os.path.join(MODEL_DIR, "meta.json"), "w", encoding="utf8") as f:
    json.dump(meta, f, indent=2)

print("Wrote demo course artifacts to:", MODEL_DIR)
print("classes:", meta["classes"])
print("vocab size:", len(vect.get_feature_names_out()))
