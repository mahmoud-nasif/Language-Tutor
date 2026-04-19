from fastapi.testclient import TestClient

from polyglot.api.version import get_app_version


def test_healthz_returns_status_and_version(client: TestClient) -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": get_app_version()}
