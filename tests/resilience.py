from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_fallback_activation():
    # Имитация поломки модели:
    original_model = app.state.model
    app.state.model = None
    payload = {"timestamp": "2026-11-27T10:00:00", "temperature": 110.0, "vibration": 8.0, "pressure": 15.0, "current": 12.5}
    res = client.post("/predict", json=payload)
    assert res.status_code == 200
    assert res.json()["source"] == "fallback_rule"
    assert res.json()["decision"] == "high_risk"
    app.state.model = original_model
