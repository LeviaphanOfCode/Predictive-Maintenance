from pydantic import BaseModel, Field, field_validator
from typing import List, Dict
from uuid import UUID
from datetime import datetime

class PredictRequest(BaseModel):
    request_id: UUID = Field(..., description="Уникальный идентификатор запроса UUIDv4")
    equipment_id: str = Field(..., description="Идентификатор оборудования")
    from_ts: datetime = Field(..., description="Начало временного окна")
    to_ts: datetime = Field(..., description="Конец временного окна")
    telemetry: Dict[str, List[float]] = Field(..., description="Временные ряды датчиков")

    @field_validator("telemetry")
    @classmethod
    def validate_telemetry_channels(cls, v):
        required_channels = ["temperature", "pressure", "vibration", "humidity"]
        for channel in required_channels:
            if channel not in v:
                raise ValueError(f"Missing required telemetry channel: {channel}")
            if len(v[channel]) != 60:
                raise ValueError(f"Channel {channel} must contain exactly 60 data points")
        return v

class TopKItem(BaseModel):
    cls: str
    prob: float

class PredictResponse(BaseModel):
    request_id: UUID
    equipment_id: str
    predicted_class: str
    confidence: float
    top_k: List[TopKItem]
    fallback_triggered: bool
    model_version: str

