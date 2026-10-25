"""Unit tests for /health endpoint (Kubernetes probes and container health checks)."""

import json


def test_health_check_healthy(client):
    """Test health check returns UP and database connected."""
    response = client.get("/health")
    assert response.status_code == 200
    data = json.loads(response.data)

    assert data["service"] == "EventEase"
    assert data["status"] == "UP"
    assert data["version"] == "1.0.0"
    assert data["database"] == "connected"
    assert "timestamp" in data


def test_health_check_unhealthy(monkeypatch, client):
    """Test health check handles database failures gracefully with HTTP 503."""
    def mock_get_db():
        raise RuntimeError("Simulated database outage")

    # Monkeypatch get_db to simulate database connection failure
    monkeypatch.setattr("app.sqlite3.connect", lambda *args, **kwargs: mock_get_db())

    # We need a new client request context without cached g.db
    with client:
        response = client.get("/health")
        assert response.status_code == 503
        data = json.loads(response.data)
        assert data["status"] == "DOWN"
        assert "unhealthy" in data["database"]
