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
            failure_prob = self.engine.predict_probabilities(prepared_data)
        except Exception as e:
            raise RuntimeError(f"Inference Engine crashed: {str(e)}")

        normal_prob = 1.0 - failure_prob
        warning_prob = failure_prob * 0.3
        
        if failure_prob > 0.5:
            predicted_class = "failure"
            confidence = failure_prob
        elif failure_prob > 0.2:
            predicted_class = "warning"
            confidence = 1.0 - failure_prob
        else:
            predicted_class = "normal"
            confidence = normal_prob

        fallback_triggered = False
        if confidence < self.threshold:
            fallback_triggered = True
            predicted_class = "failure" 
            confidence = failure_prob

        top_k = [
            TopKItem(cls="failure", prob=round(failure_prob, 3)),
            TopKItem(cls="warning", prob=round(warning_prob, 3)),
            TopKItem(cls="normal", prob=round(max(0.0, normal_prob - warning_prob), 3))
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

