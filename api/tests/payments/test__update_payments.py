from fastapi.testclient import TestClient
from api.main import app
import pytest

client = TestClient(app)

# payments/{payment_id}


def test_update_payment(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_payment = {
        "user_id": 1,
        "amount": 200,
        "method": "updatedmethod",
        "completed": False,
        "refund_requested": False
    }
    response = client.put("/payments/1", json=fake_payment, headers=headers)
    assert response.status_code == 200

    client, headers = client_with_token("superadmin")
    response = client.get("/payments/1", headers=headers)
    assert response.status_code == 200

    assert response.json()["method"] == "updatedmethod"


def test_update_payment_missing_field(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_payment = {
        "user_id": 1,
        "amount": 200,
        "method": "updatedmethod",
        "completed": False,
    }
    response = client.put("/payments/1", json=fake_payment, headers=headers)
    assert response.status_code == 422


def test_update_payment_wrong_data_type(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_payment = {
        "user_id": 1,
        "amount": 200,
        "method": "updatedmethod",
        "completed": False,
        "refund_requested": 500
    }
    response = client.put("/payments/1", json=fake_payment, headers=headers)
    assert response.status_code == 422


def test_update_payment_nonexistent_user(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_payment = {
        "user_id": 10000,
        "amount": 200,
        "method": "updatedmethod",
        "completed": False,
        "refund_requested": False
    }
    response = client.put("/payments/1", json=fake_payment, headers=headers)
    assert response.status_code == 404


def test_update_payment_nonexistent_payment(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_payment = {
        "user_id": 1,
        "amount": 200,
        "method": "updatedmethod",
        "completed": False,
        "refund_requested": False
    }
    response = client.put("/payments/1000000",
                          json=fake_payment, headers=headers)
    assert response.status_code == 404


def test_update_payment_no_authorization(client_with_token):
    client, headers = client_with_token("user")
    fake_payment = {
        "user_id": 1,
        "amount": 200,
        "method": "updatedmethod",
        "completed": False,
        "refund_requested": False
    }
    response = client.put("/payments/1", json=fake_payment, headers=headers)
    assert response.status_code == 401


def test_update_payment_no_header(client):
    fake_payment = {
        "user_id": 1,
        "amount": 200,
        "method": "updatedmethod",
        "completed": False,
        "refund_requested": False
    }
    response = client.put("/payments/1", json=fake_payment)
    assert response.status_code == 401


# payments/{payment_id}/request_refund (not paid for yet)
def test_request_refund_not_paid_yet(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_payment = {}
    response = client.post("payments/1/request_refund",
                           json=fake_payment, headers=headers)
    assert response.status_code == 400


# payments/{payment_id}/pay
def test_pay_payment(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_payment = {}
    response = client.post("payments/1/pay",
                           json=fake_payment, headers=headers)
    assert response.status_code == 200

    client, headers = client_with_token("superadmin")
    response = client.get("/payments/1", headers=headers)
    assert response.status_code == 200

    assert response.json()["completed"] is True


def test_pay_payment_already_paid(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_payment = {}
    response = client.post("payments/1/pay",
                           json=fake_payment,
                           headers=headers)
    assert response.status_code == 400


def test_pay_nonexistent_payment(client_with_token):
    client, headers = client_with_token("paymentadmin")
    fake_payment = {}
    response = client.post("payments/43232/pay",
                           json=fake_payment, headers=headers)
    assert response.status_code == 404


def test_pay_payment_not_users_payment(client_with_token):
    client, headers = client_with_token("paymentadmin")
    fake_payment = {}
    response = client.post("payments/1/pay",
                           json=fake_payment, headers=headers)
    assert response.status_code == 403


def test_pay_payment_no_header(client):
    fake_payment = {}
    response = client.post("payments/1/pay", json=fake_payment)
    assert response.status_code == 401


# payments/{user_id}/request_refund
@pytest.mark.dependency(name="request_refund_created")
def test_request_refund(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_payment = {}
    response = client.post("payments/1/request_refund",
                           json=fake_payment, headers=headers)
    assert response.status_code == 200

    client, headers = client_with_token("superadmin")
    response = client.get("/payments/1", headers=headers)
    assert response.status_code == 200

    assert response.json()["refund_requested"] is True


def test_request_refund_already_requested(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_payment = {}
    response = client.post("payments/1/request_refund",
                           json=fake_payment, headers=headers)
    assert response.status_code == 400


def test_request_refund_not_own_payment(client_with_token):
    client, headers = client_with_token("admin")
    fake_payment = {}
    response = client.post("payments/1/request_refund",
                           json=fake_payment, headers=headers)
    assert response.status_code == 403


def test_request_refund_nonexistent_id(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_payment = {}
    response = client.post("payments/452543534/request_refund",
                           json=fake_payment, headers=headers)
    assert response.status_code == 404


def test_request_refund_no_header(client):
    fake_payment = {}
    response = client.post("payments/1/request_refund", json=fake_payment)
    assert response.status_code == 401


# GET payments/refunds
@pytest.mark.dependency(depends=["request_refund_created"])
def test_get_refunds(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/refunds", headers=headers)
    print(response.text)
    assert response.status_code == 200


@pytest.mark.dependency(depends=["request_refund_created"])
def test_get_refunds_with_user(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/refunds?user_id=1", headers=headers)
    assert response.status_code == 200


def test_get_refunds_nonexistent_user(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/refunds?user_id=32427368542",
                          headers=headers)
    assert response.status_code == 404


def test_get_refunds_no_authorization(client_with_token):
    client, headers = client_with_token("user")
    response = client.get("/payments/refunds", headers=headers)
    assert response.status_code == 403


def test_get_refunds_no_header(client):
    response = client.get("/payments/refunds")
    assert response.status_code == 401
