import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.models.user_model import UserModel
from api.models.payment_model import PaymentModel
from api.datatypes.payment import PaymentCreate


client = TestClient(app)
user_model = UserModel()
payment_model = PaymentModel()


@pytest.fixture
def seeded_payments():
    user = user_model.get_user_by_username("superadmin")
    if not user:
        raise Exception("Superadmin must exist in the DB for benchmarks")
    
    #zorgt dat er 5 payments zijn minimaal
    existing = payment_model.get_payments_by_user(user.id)
    if len(existing) < 5:
        for i in range(5 - len(existing)):
            p = PaymentCreate(
                user_id=user.id,
                amount=100 + i,
            )
    payment_model.create_payment(p)


@pytest.mark.benchmark(group="payments")
def test_get_my_payments_performance(benchmark, client_with_token, seeded_payments):
    client, headers = client_with_token("superadmin")

    def get_my_payments():
        return client.get("/payments/me", headers=headers)

    result = benchmark(get_my_payments)

    assert result.status_code == 200

@pytest.mark.benchmark(group="payments")
def test_get_my_open_payments_performance(benchmark, client_with_token, seeded_payments):
    client, headers = client_with_token("superadmin")

    def get_my_open_payments():
        return client.get("/payments/me/open", headers=headers)

    result = benchmark(get_my_open_payments)

    assert result.status_code == 200
