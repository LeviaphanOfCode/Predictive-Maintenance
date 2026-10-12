import numpy as np
from app.api.schemas import PredictRequest
from app.core.config import settings

class TargetScaler:
    def __init__(self):
        self.mins = np.array(settings.SCALER_MINS)
        self.maxs = np.array(settings.SCALER_MAXS)

    def transform(self, x: np.ndarray) -> np.ndarray:
        return (x - self.mins) / (self.maxs - self.mins + 1e-9)

class Preprocessor:
    def __init__(self):
        self.scaler = TargetScaler()

    def process(self, request: PredictRequest) -> np.ndarray:
        features = [
            np.mean(request.telemetry["temperature"]),
            np.mean(request.telemetry["pressure"]),
            np.mean(request.telemetry["vibration"]),
            np.mean(request.telemetry["humidity"])
        ]
        
        equipment_type = request.equipment_id.split("_")[0]
        if equipment_type == "TURBINE":
            eq_features = [1.0, 0.0, 0.0]
        elif equipment_type == "PUMP":
            eq_features = [0.0, 1.0, 0.0]
        else:
            eq_features = [0.0, 0.0, 1.0]
            
        full_features = np.array(features + eq_features, dtype=np.float32)
        full_features[:4] = self.scaler.transform(full_features[:4])
        return full_features.reshape(1, -1)

