import pytest
from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


@pytest.mark.benchmark(group="payments")
def test_get_my_payments_performance(benchmark, client_with_token):
    client, headers = client_with_token("superadmin")
    def get_my_payments():
        return client.get("/payments/me", headers=headers)

    result = benchmark(get_my_payments)
    assert result.status_code == 200

@pytest.mark.benchmark(group="payments")
def test_get_my_open_payments_performance(benchmark, client_with_token):
    client, headers = client_with_token("superadmin")
    def get_my_open_payments():
        return client.get("/payments/me/open", headers=headers)

    result = benchmark(get_my_open_payments)
    assert result.status_code == 200
