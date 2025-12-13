import pytest
from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


@pytest.mark.benchmark(group="user")
def test_login_success_performance(benchmark):
    payload = {
        "username": "superadmin",
        "password": "admin123"
    }

    def do_login():
        return client.post("/login", json=payload)

    result = benchmark(do_login)

    assert result.status_code == 200


@pytest.mark.benchmark(group="user")
def test_profile_performance(benchmark, client_with_token):
    client, headers = client_with_token("superadmin")

    def get_profile():
        return client.get("/profile", headers=headers)

    result = benchmark(get_profile)

    assert result.status_code == 200
