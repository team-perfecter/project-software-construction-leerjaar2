"""
this file contains all tests related to update payments endpoints.
"""

from unittest.mock import patch
from api.tests.conftest import get_last_payment_id


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
    response = client.put(f"/payments/{payment_id}", json=fake_payment, headers=headers)
    assert response.status_code == 422


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
    client, headers = client_with_token("user")
    fake_payment = {
        "user_id": 1,
        "amount": 200,
        "method": "updatedmethod",
        "completed": False,
        "refund_requested": False
    }
    response = client.put("/payments/1", json=fake_payment, headers=headers)
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
