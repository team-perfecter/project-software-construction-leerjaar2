"""
this file contains all tests related to delete payments endpoints.
"""

from unittest.mock import patch
from api.tests.conftest import get_last_payment_id




# /payments/{payment_id}
@patch("api.models.payment_model.PaymentModel.delete_payment",
       return_value=False)
def test_delete_payment_server_error(mock_create, client_with_token):
    """Simulates a server error when attempting to delete a payment.

    Args:
        mock_create: Mocked delete_payment method to force a failure.
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 500.
    """
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("superadmin")
    response = client.delete(f"/payments/{payment_id}", headers=headers)
    assert response.status_code == 500


def test_delete_payment_by_id(client_with_token):
    """Deletes a payment by its ID successfully and verifies it no longer exists.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If deletion fails or the payment still exists.
    """
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("superadmin")
    response = client.delete(f"/payments/{payment_id}", headers=headers)
    assert response.status_code == 200

    client, headers = client_with_token("superadmin")
    response = client.get("/payments/1", headers=headers)
    assert response.status_code == 404


def test_delete_payment_by_id_not_int(client_with_token):
    """Attempts to delete a payment using a non-integer ID.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 422.
    """
    client, headers = client_with_token("superadmin")
    response = client.delete("/payments/hallo", headers=headers)
    assert response.status_code == 422


def test_delete_payment_by_nonexistent_id(client_with_token):
    """Attempts to delete a payment with an ID that does not exist.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    client, headers = client_with_token("superadmin")
    response = client.delete("/payments/1000", headers=headers)
    assert response.status_code == 404


def test_delete_payment_by_id_no_authorization(client_with_token):
    """Attempts to delete a payment as a user without proper permissions.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 403.
    """
    client, headers = client_with_token("user")
    response = client.delete("/payments/1", headers=headers)
    assert response.status_code == 403


def test_delete_payment_by_id_no_header(client):
    """Attempts to delete a payment without providing authentication headers.

    Args:
        client: TestClient instance.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
    response = client.delete("/payments/1")
    assert response.status_code == 401
