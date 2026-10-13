# -*- coding: utf-8 -*-
import numpy as np
from app.api.schemas import PredictRequest, PredictResponse, TopKItem
from app.ml.preprocessing import Preprocessor
from app.ml.inference import InferenceEngine
from app.core.config import settings

class PredictiveMaintenanceService:
    def __init__(self, inference_engine: InferenceEngine):
        self.preprocessor = Preprocessor()
        self.engine = inference_engine
        self.threshold = settings.FALLBACK_THRESHOLD

    def run_prediction(self, request: PredictRequest) -> PredictResponse:
        prepared_data = self.preprocessor.process(request)
        
        try:
            probs = self.engine.predict_probabilities(prepared_data)
        except FileNotFoundError as e:
            raise e
        except Exception as e:
            raise RuntimeError(f"Inference Engine crashed: {str(e)}")

        max_idx = int(np.argmax(probs))
        predicted_class = settings.CLASSES[max_idx]
        confidence = float(probs[max_idx])

        fallback_triggered = False
        if confidence < self.threshold:
            fallback_triggered = True
            predicted_class = "critical"
            confidence = float(probs[settings.CLASSES.index("critical")])

        top_k = [
            TopKItem(cls=settings.CLASSES[i], prob=round(float(probs[i]), 3))
            for i in range(len(settings.CLASSES))
        ]
        top_k.sort(key=lambda item: item.prob, reverse=True)

        return PredictResponse(
            request_id=request.request_id,
            equipment_id=request.equipment_id,
            predicted_class=predicted_class,
            confidence=round(confidence, 3),
            top_k=top_k,
            fallback_triggered=fallback_triggered,
            model_version=self.engine.model_version
        )
