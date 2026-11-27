from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_predict_success():
    payload = {"timestamp": "2026-11-27T10:00:00", "temperature": 75.0, "vibration": 3.0, "pressure": 15.0, "current": 12.5}
    res = client.post("/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "trace_id" in data
    assert data["source"] in ["model", "fallback_rule"]

def test_validation_error():
    payload = {"timestamp": "2026-11-27T10:00:00", "temperature": 75.0, "vibration": 3.0, "pressure": -5.0, "current": 12.5}
    res = client.post("/predict", json=payload)
    assert res.status_code == 422
