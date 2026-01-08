"""
this file contains all tests related to post payments endpoints.
"""

from unittest.mock import patch


def test_create_payment_with_superadmin(client_with_token):
    """Creates a new payment as a superadmin.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the payment is not created successfully.
    """
    client, headers = client_with_token("superadmin")
    fake_payment = {
        "user_id": 1,
        "amount": 200,
        "method": "method1"
    }
    response = client.post("/payments", json=fake_payment, headers=headers)
    assert response.status_code == 201


def test_create_payment_with_paymentadmin(client_with_token):
    """Creates a new payment as a payment admin.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the payment is not created successfully.
    """
    client, headers = client_with_token("paymentadmin")
    fake_payment = {
        "user_id": 1,
        "amount": 100,
        "method": "method2"
    }
    response = client.post("/payments", json=fake_payment, headers=headers)
    assert response.status_code == 201


@patch("api.models.payment_model.PaymentModel.create_payment",
       return_value=False)
def test_create_payment_server_error(mock_create, client_with_token):
    """Handles a server error during payment creation.

    Args:
        mock_create: Mocked create_payment method returning False.
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 500.
    """
    client, headers = client_with_token("superadmin")
    fake_payment = {
        "user_id": 1,
        "amount": 200,
        "method": "method1"
    }
    response = client.post("/payments", json=fake_payment, headers=headers)
    assert response.status_code == 500


def test_create_payment_without_authorization(client_with_token):
    """Attempts to create a payment with insufficient permissions.

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
        "amount": 100,
        "method": "method3"
    }
    response = client.post("/payments", json=fake_payment, headers=headers)
    assert response.status_code == 403


def test_create_payment_no_token(client):
    """Attempts to create a payment without authentication.

    Args:
        client: Unauthenticated test client.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
    fake_payment = {
        "user_id": 1,
        "amount": 100,
        "method": "method4"
    }
    response = client.post("/payments", json=fake_payment)
    assert response.status_code == 401


def test_create_payment_missing_field(client_with_token):
    """Attempts to create a payment with missing required fields.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 422.
    """
    client, headers = client_with_token("superadmin")
    fake_payment = {
        "user_id": 1,
        "method": "method5"
    }
    response = client.post("/payments", json=fake_payment, headers=headers)
    assert response.status_code == 422


def test_create_payment_wrong_data_type(client_with_token):
    """Attempts to create a payment with incorrect data types.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 422.
    """
    client, headers = client_with_token("superadmin")
    fake_payment = {
        "user_id": 1,
        "amount": 1,
        "method": 123
    }
    response = client.post("/payments", json=fake_payment, headers=headers)
    assert response.status_code == 422
