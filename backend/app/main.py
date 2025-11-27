# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware     # <-- make sure this line is present
from app.api import router as api_router
from app.model import load_artifacts

app = FastAPI(title="CreditRiskAPI", version="0.1")

# CORS middleware (dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend origin (or ["*"] for quick dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    load_artifacts()

app.include_router(api_router, prefix="")

@app.get("/health")
def health():
    return {"status": "ok"}
