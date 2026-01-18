import pytest
from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


@pytest.mark.benchmark(group="discount-codes")
def test_get_my_discount_codes_performance(benchmark, client_with_token):
    client, headers = client_with_token("superadmin")
    def get_my_discount_codes():
        return client.get("/discount-codes/", headers=headers)

    result = benchmark(get_my_discount_codes)
    assert result.status_code == 200

@pytest.mark.benchmark(group="discount-codes")
def test_get_my_open_discount_codes_performance(benchmark, client_with_token):
    client, headers = client_with_token("superadmin")
    def get_my_open_discount_codes():
        return client.get("/discount-codes/active", headers=headers)

    result = benchmark(get_my_open_discount_codes)
    assert result.status_code == 200