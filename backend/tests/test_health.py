def test_root_returns_app_metadata(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["app"] == "jacer"
    assert body["status"] == "ok"
    assert "version" in body


def test_health_endpoint_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
