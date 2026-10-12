import pytest
from uuid import uuid4
from datetime import datetime, timezone
from app.api.schemas import PredictRequest, PredictResponse
from app.ml.inference import InferenceEngine
from app.services.prediction import PredictiveMaintenanceService

@pytest.fixture
def mock_telemetry():
    return {
        "temperature": [65.0] * 60,
        "pressure": [30.0] * 60,
        "vibration": [12.0] * 60,
        "humidity": [45.0] * 60
    }

@pytest.fixture
def service():
    engine = InferenceEngine(weights_path=None)
    return PredictiveMaintenanceService(engine)

def test_successful_inference_schema(service, mock_telemetry):
    req = PredictRequest(
        request_id=uuid4(),
        equipment_id="TURBINE_UNIT_01",
        from_ts=datetime.now(timezone.utc),
        to_ts=datetime.now(timezone.utc),
        telemetry=mock_telemetry
    )
    res = service.run_prediction(req)
    assert isinstance(res, PredictResponse)
    assert res.model_version == "1.3.0"

def test_anomaly_input_changes_behavior(service):
    bad_telemetry = {
        "temperature": [195.0] * 60,
        "pressure": [95.0] * 60,
        "vibration": [48.0] * 60,
        "humidity": [80.0] * 60
    }
    req = PredictRequest(
        request_id=uuid4(),
        equipment_id="PUMP_UNIT_42",
        from_ts=datetime.now(timezone.utc),
        to_ts=datetime.now(timezone.utc),
        telemetry=bad_telemetry
    )
    res = service.run_prediction(req)
    assert res.predicted_class == "failure"

def test_invalid_telemetry_length_raises_error(mock_telemetry):
    mock_telemetry["temperature"] = [65.0] * 10
    with pytest.raises(ValueError):
        PredictRequest(
            request_id=uuid4(),
            equipment_id="PUMP_UNIT_42",
            from_ts=datetime.now(timezone.utc),
            to_ts=datetime.now(timezone.utc),
            telemetry=mock_telemetry
        )

def test_inference_engine_failure_handling():
    with pytest.raises(FileNotFoundError):
        InferenceEngine(weights_path="corrupted_weights.npy")

