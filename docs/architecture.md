```markdown
# Architecture Overview

This prototype uses a modular architecture:

- Data & Model
  - Training script (PyTorch autoencoder) produces model.pt, scaler.joblib, and meta.json with threshold values.
  - The detector uses reconstruction error per flow as an anomaly score.

- Backend (FastAPI)
  - Endpoints:
    - POST /predict — score a single network flow (JSON features) and return anomaly_score, label, per-feature reconstruction errors.
    - POST /predict/batch — batch predictions
    - POST /simulate_stream — optional: stream a sequence of flows for demo (returns streamed results)
    - GET /metrics — model evaluation & threshold summary
    - GET /health — liveness
  - Loads model and scaler at startup. Uses numpy + PyTorch for inference.

- Frontend (React)
  - Small dashboard to submit flows, show the anomaly score and explanation, and plot a simple history.

Deployment
- docker-compose for local integration: backend + frontend
- Production: run backend behind API gateway with TLS, authentication, logging, monitoring, and restricted access to model artifacts.

Security & Governance
- Validate and sanitize all incoming flow fields.
- Don't log or persist PII or payloads containing private data.
- Keep model and training data in a secure registry; use versioning (MLflow, DVC).