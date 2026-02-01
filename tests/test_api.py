from fastapi.testclient import TestClient

from src.main import app


def test_health_endpoint():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_task_endpoint_runs_example_task():
    client = TestClient(app)
    payload = {
        "tasks": ["example"],
        "options": {
            "example": {
                "params": {"data": 123},
            }
        },
    }

    resp = client.post("/api/task", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert "results" in data
    assert len(data["results"]) == 1
    result = data["results"][0]
    assert result["name"] == "example"
    assert result["passed"] is True
    assert result["details"]["data"] == 123
