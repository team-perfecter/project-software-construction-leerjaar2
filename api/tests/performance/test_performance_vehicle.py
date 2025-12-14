import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.tests.conftest import get_last_vid


client = TestClient(app)


@pytest.mark.benchmark(group="vehicles")
def test_get_my_vehicles_performance(benchmark, client_with_token):
    client, headers = client_with_token("superadmin")
    def get_my_vehicles():
        return client.get("/vehicles", headers=headers)

    result = benchmark(get_my_vehicles)
    assert result.status_code == 200


@pytest.mark.benchmark(group="vehicles")
def test_get_vehicles_by_id_performance(benchmark, client_with_token):
    vid = get_last_vid(client_with_token)
    client, headers = client_with_token("superadmin")
    def get_vehicles_by_id():
        return client.get(f"/vehicles/{vid}", headers=headers)

    result = benchmark(get_vehicles_by_id)
    assert result.status_code == 200


@pytest.mark.benchmark(group="vehicles")
def test_get_vehicles_by_user_id_performance(benchmark, client_with_token):
    client, headers = client_with_token("superadmin")
    def get_vehicles_by_user_id():
        return client.get("/vehicles/user/1", headers=headers)

    result = benchmark(get_vehicles_by_user_id)
    assert result.status_code == 200
