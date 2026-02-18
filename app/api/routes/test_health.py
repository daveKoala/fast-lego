from fastapi.testclient import TestClient

from app.api.routes import health
from app.main import app

client = TestClient(app)


def test_health_ok(monkeypatch):
    monkeypatch.setattr(health, "check_database_connection", lambda: (True, "healthy"))

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert "x-request-id" in response.headers
    assert payload["data"]["status"] == "ok"
    assert payload["data"]["database"]["connected"] is True


def test_health_degraded(monkeypatch):
    monkeypatch.setattr(health, "check_database_connection", lambda: (False, "down"))
    monkeypatch.setattr(health.settings, "debug", False)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["status"] == "degraded"
    assert payload["data"]["database"]["connected"] is False
    assert payload["data"]["database"]["details"] == "Database connection failed"


def test_health_degraded_in_debug_returns_error_details(monkeypatch):
    monkeypatch.setattr(health, "check_database_connection", lambda: (False, "down"))
    monkeypatch.setattr(health.settings, "debug", True)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["status"] == "degraded"
    assert payload["data"]["database"]["details"] == "down"


def test_health_propagates_incoming_request_id(monkeypatch):
    monkeypatch.setattr(health, "check_database_connection", lambda: (True, "healthy"))

    response = client.get("/health", headers={"x-request-id": "req-123"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-123"


def test_not_found_uses_standard_error_payload():
    response = client.get("/missing-page")

    assert response.status_code == 404
    payload = response.json()
    assert set(payload.keys()) == {"message", "action", "x-request-id"}
    assert payload["action"] == "modify_request"
    assert isinstance(payload["x-request-id"], str)
