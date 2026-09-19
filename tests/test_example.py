from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_and_list_example():
    res = client.post("/api/examples/", json={"name": "test"})
    assert res.status_code == 200
    assert res.json()["name"] == "test"

    res = client.get("/api/examples/")
    assert res.status_code == 200
    assert any(item["name"] == "test" for item in res.json())
