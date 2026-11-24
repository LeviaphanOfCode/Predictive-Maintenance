import uuid, time, joblib, pandas as pd
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from app.api.schemas import TelemetryRequest, PredictionResponse
from app.api.logger import get_json_logger

logger = get_json_logger("pump_api")
MODEL_VERSION = "v1.4.0"

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.preprocessor = joblib.load("artifacts/preprocessor.joblib")
        app.state.model = joblib.load("models/model.joblib")
    except Exception as e:
        logger.error(f"Ошибка загрузки весов: {e}")
        app.state.model = None
    yield

app = FastAPI(title="Resilient Pump API", version=MODEL_VERSION, lifespan=lifespan)

@app.post("/predict", response_model=PredictionResponse)
def predict(req: TelemetryRequest):
    start = time.perf_counter()
    trace_id = str(uuid.uuid4())
    source = "model"

    try:
        if app.state.model is None:
            raise RuntimeError("Модель не инициализирована")
        df = pd.DataFrame([req.model_dump()])
        X = app.state.preprocessor.transform(df)
        prob = float(app.state.model.predict_proba(X)[0, 1])
    except Exception as exc:
        # ПАТТЕРН FALLBACK: резервная пороговая эвристика при аварии
        source = "fallback_rule"
        prob = 1.0 if req.vibration > 6.0 or req.temperature > 95.0 else 0.0

    latency = round((time.perf_counter() - start) * 1000, 2)
    decision = "high_risk" if prob >= 0.70 else "normal"

    # Структурированный лог в формате JSON:
    rec = logger.makeRecord("pump_api", logging.INFO, "", 0, "inference", (), None)
    rec.extra_data = {
        "trace_id": trace_id, "device_id": req.device_id,
        "prob": round(prob, 4), "decision": decision,
        "source": source, "latency_ms": latency
    }
    logger.handle(rec)

    return PredictionResponse(
        trace_id=trace_id, device_id=req.device_id,
        failure_probability=round(prob, 4), decision=decision,
        model_version=MODEL_VERSION, source=source, latency_ms=latency
    )
