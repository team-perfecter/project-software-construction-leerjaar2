"""
this file contains all tests related to update payments endpoints.
"""

from unittest.mock import patch
from api.main import app
import pytest
from api.tests.conftest import get_last_payment_id, get_last_pid


client = TestClient(app)


# payments/{payment_id}
def test_update_payment(client_with_token):
    """Updates a payment successfully and verifies the changes.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If update fails or the payment data is incorrect.
    """
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("superadmin")
    fake_payment = {
        "user_id": 1,
        "transaction": "transaction1",
        "amount": 200,
        "method": "updatedmethod",
        "issuer": "issuer1",
        "hash": "a",
        "bank": "bank1",
        "completed": False,
        "refund_requested": False
    }
    response = client.put(f"/payments/{payment_id}", json=fake_payment,
                          headers=headers)
    assert response.status_code == 200

    client, headers = client_with_token("superadmin")
    response = client.get(f"/payments/{payment_id}", headers=headers)
    assert response.status_code == 200

    assert response.json()["method"] == "updatedmethod"


@patch("api.models.payment_model.PaymentModel.update_payment",
       return_value=False)
def test_update_payment_server_error(mock_create, client_with_token):
    """Simulates a server error when updating a payment.

    Args:
        mock_create: Mocked update_payment method to force a failure.
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 500.
    """
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("superadmin")
    fake_payment = {
        "user_id": 1,
        "transaction": "transaction1",
        "amount": 200,
        "method": "updatedmethod",
        "issuer": "issuer1",
        "bank": "bank1",
        "completed": False,
        "refund_requested": False
    }
    response = client.put(f"/payments/{payment_id}", json=fake_payment,
                          headers=headers)
    assert response.status_code == 500


def test_update_payment_missing_field(client_with_token):
    """Attempts to update a payment with a missing required field.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 422.
    """
    client, headers = client_with_token("superadmin")
    payment_id = get_last_payment_id(client_with_token)
    fake_payment = {}
    response = client.put(f"/payments/{payment_id}", json=fake_payment,
                          headers=headers)
    assert response.status_code == 500


def test_update_payment_wrong_data_type(client_with_token):
    """Attempts to update a payment with an incorrect data type.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 422.
    """
    client, headers = client_with_token("superadmin")
    fake_payment = {
        "amount": 200,
        "method": "updatedmethod",
        "completed": False,
        "refund_requested": 500
    }
    response = client.put("/payments/1", json=fake_payment, headers=headers)
    assert response.status_code == 422


def test_update_payment_nonexistent_user(client_with_token):
    """Attempts to update a payment for a user that does not exist.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
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
    """Attempts to update a payment that does not exist.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
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
    """Attempts to update a payment as a user without permission.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 403.
    """
    client, headers = client_with_token("superadmin")
    pid = get_last_pid(client)
    fake_payment = {
        "user_id": 1,
        "parking_lot_id": pid,
        "amount": 200,
        "method": "method1"
    }
    client.post("/payments", json=fake_payment, headers=headers)
    client, headers = client_with_token("user")
    payment_id = get_last_payment_id(client_with_token)
    fake_payment = {
        "user_id": 1,
        "amount": 200,
        "method": "updatedmethod",
        "completed": False,
        "refund_requested": False
    }
    response = client.put(f"/payments/{payment_id}", json=fake_payment,
                          headers=headers)
    assert response.status_code == 403


def test_update_payment_no_header(client):
    """Attempts to update a payment without authentication headers.

    Args:
        client: TestClient instance.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
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
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("superadmin")
    response = client.post(f"payments/{payment_id}/request_refund",
                           json={}, headers=headers)
    assert response.status_code == 400


# payments/{payment_id}/pay
@patch("api.models.payment_model.PaymentModel.mark_payment_completed",
       return_value=False)
def test_pay_payment_server_error(mock_create, client_with_token):
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("superadmin")
    response = client.post(f"/payments/{payment_id}/pay", json={},
                           headers=headers)
    assert response.status_code == 500


def test_pay_payment(client_with_token):
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("superadmin")
    response = client.post(f"payments/{payment_id}/pay",
                           json={}, headers=headers)
    assert response.status_code == 200

    client, headers = client_with_token("superadmin")
    response = client.get(f"/payments/{payment_id}", headers=headers)
    assert response.status_code == 200

    assert response.json()["completed"] is True


def test_pay_payment_already_paid(client_with_token):
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("superadmin")
    client.post(f"/payments/{payment_id}/pay", json={}, headers=headers)
    response = client.post(f"payments/{payment_id}/pay",
                           json={},
                           headers=headers)
    assert response.status_code == 400


def test_pay_nonexistent_payment(client_with_token):
    client, headers = client_with_token("paymentadmin")
    response = client.post("payments/43232/pay",
                           json={}, headers=headers)
    assert response.status_code == 404


def test_pay_payment_not_users_payment(client_with_token):
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("paymentadmin")
    response = client.post(f"payments/{payment_id}/pay",
                           json={}, headers=headers)
    assert response.status_code == 403


def test_pay_payment_not_users_payment_guest(client_with_token, client):
    payment_id = get_last_payment_id(client_with_token)
    headers = {"Authorization": "Bearer"}
    response = client.post(f"/payments/{payment_id}/pay", json={}, headers=headers)
    assert response.status_code == 403


def test_pay_payment_no_header(client):
    fake_payment = {}
    response = client.post("payments/1/pay", json=fake_payment)
    assert response.status_code == 401


# payments/{user_id}/request_refund
@patch("api.models.payment_model.PaymentModel.mark_refund_request",
       return_value=False)
def test_request_refund_server_error(mock_create, client_with_token):
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("superadmin")
    client.post(f"/payments/{payment_id}/pay", json={}, headers=headers)
    response = client.post(f"payments/{payment_id}/request_refund",
                           json={}, headers=headers)
    assert response.status_code == 500


def test_request_refund(client_with_token):
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("superadmin")
    client.post(f"/payments/{payment_id}/pay", json={}, headers=headers)
    response = client.post(f"payments/{payment_id}/request_refund",
                           json={}, headers=headers)
    assert response.status_code == 200

    client, headers = client_with_token("superadmin")
    response = client.get(f"/payments/{payment_id}", headers=headers)
    assert response.status_code == 200

    assert response.json()["refund_requested"] is True


def test_request_refund_already_requested(client_with_token):
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("superadmin")
    client.post(f"/payments/{payment_id}/pay", json={}, headers=headers)
    client.post(f"payments/{payment_id}/request_refund",
                json={}, headers=headers)

    client, headers = client_with_token("superadmin")
    response = client.post(f"payments/{payment_id}/request_refund",
                           json={}, headers=headers)

    assert response.status_code == 400


def test_request_refund_not_own_payment(client_with_token):
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("lotadmin")
    response = client.post(f"payments/{payment_id}/request_refund",
                           json={}, headers=headers)
    assert response.status_code == 403


def test_request_refund_nonexistent_id(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.post("payments/452543534/request_refund",
                           json={}, headers=headers)
    assert response.status_code == 404


def test_request_refund_no_header(client):
    response = client.post("payments/1/request_refund", json={})
    assert response.status_code == 401


# POST payments/{id}/give_refund
@patch("api.models.payment_model.PaymentModel.give_refund",
       return_value=False)
def test_give_refund_server_error(mock_create, client_with_token):
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("superadmin")
    client.post(f"/payments/{payment_id}/pay", json={}, headers=headers)
    response = client.post(f"payments/{payment_id}/give_refund",
                           json={}, headers=headers)
    assert response.status_code == 500


def test_give_refund(client_with_token):
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("superadmin")
    client.post(f"/payments/{payment_id}/pay", json={}, headers=headers)
    response = client.post(f"payments/{payment_id}/give_refund",
                           json={}, headers=headers)
    assert response.status_code == 200

    client, headers = client_with_token("superadmin")
    response = client.get(f"/payments/{payment_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["refund_accepted"] is True
    assert response.json()["admin_id"] is not None


def test_give_refund_no_lot_access(client_with_token):
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("superadmin")
    client.post(f"/payments/{payment_id}/pay", json={}, headers=headers)
    response = client.post(f"payments/{payment_id}/give_refund",
                           json={}, headers=headers)
    assert response.status_code == 200

    client, headers = client_with_token("lotadmin")
    response = client.post(f"/payments/{payment_id}/give_refund",
                           headers=headers)
    assert response.status_code == 403


def test_give_refund_not_paid_yet(client_with_token):
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("superadmin")
    response = client.post(f"payments/{payment_id}/give_refund",
                           json={}, headers=headers)
    assert response.status_code == 400


def test_give_refund_not_found(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.post(f"payments/{2423235343}/give_refund",
                           json={}, headers=headers)
    assert response.status_code == 404


def test_give_refund_already_refunded(client_with_token):
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("superadmin")
    client.post(f"/payments/{payment_id}/pay", json={}, headers=headers)
    response = client.post(f"payments/{payment_id}/give_refund",
                           json={}, headers=headers)
    assert response.status_code == 200

    client, headers = client_with_token("superadmin")
    response = client.post(f"payments/{payment_id}/give_refund",
                           json={}, headers=headers)
    assert response.status_code == 400


# GET payments/refunds
def test_get_refunds(client_with_token):
    client, headers = client_with_token("superadmin")
    payment_id = get_last_payment_id(client_with_token)
    client.post(f"/payments/{payment_id}/pay", json={},
                headers=headers)
    client.post(f"payments/{payment_id}/request_refund",
                json={}, headers=headers)
    response = client.get("/payments/refunds", headers=headers)
    print(response.text)
    assert response.status_code == 200


def test_get_refunds_with_user(client_with_token):
    client, headers = client_with_token("superadmin")
    payment_id = get_last_payment_id(client_with_token)
    client.post(f"/payments/{payment_id}/pay", json={}, headers=headers)
    client.post(f"payments/{payment_id}/request_refund",
                json={}, headers=headers)
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
