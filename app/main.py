from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

from app.api.schemas import PredictRequest, PredictResponse
from app.ml.inference import InferenceEngine
from app.services.prediction import PredictiveMaintenanceService
from app.core.config import settings

@asynccontextmanager
async def ls(app: FastAPI):
    engine = InferenceEngine(weights_path="models/weights.npz")
    app.state.service = PredictiveMaintenanceService(engine)
    yield

app = FastAPI(title="Predictive maintenance", version=settings.MODEL_VERSION, lifespan=ls)

@app.get("/health")
def health():
    return {"status": "ok", "model_version": settings.MODEL_VERSION}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        return app.state.service.run_prediction(req)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail="Weights file not found!") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Inference error") from exc
