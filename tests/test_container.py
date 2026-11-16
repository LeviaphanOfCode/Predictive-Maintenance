import uuid
from datetime import datetime, timezone

import requests

BASE = "http://localhost:8000"

def _payload(equipment_id="PUMP_001", n=60):
    return {
        "request_id": str(uuid.uuid4()),
        "equipment_id": equipment_id,
        "from_ts": datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat(),
        "to_ts": datetime(2026, 1, 1, 0, 1, tzinfo=timezone.utc).isoformat(),
        "telemetry": {
            "temperature": [75.0] * n,
            "pressure": [15.0] * n,
            "vibration": [3.2] * n,
            "humidity": [45.0] * n,
        },
    }

def test_container_health():
    res = requests.get(f"{BASE}/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["model_version"] == "1.4.0"

def test_container_predict():
    res = requests.post(f"{BASE}/predict", json=_payload())
    assert res.status_code == 200
    data = res.json()
    assert data["predicted_class"] in ["safe", "warning", "critical"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert isinstance(data["fallback_triggered"], bool)
    assert data["model_version"] == "1.4.0"

def test_container_predict_validation():
    bad = _payload()
    del bad["telemetry"]["humidity"]
    res = requests.post(f"{BASE}/predict", json=bad)
    assert res.status_code == 422
