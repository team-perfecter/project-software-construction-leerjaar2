"""
this file contains all tests related to get payments endpoints.
"""
from fastapi.testclient import TestClient
from api.main import app
from api.tests.conftest import get_last_payment_id, get_last_pid

client = TestClient(app)


# /payments/{payment_id}
def test_get_payment_by_id(client_with_token):
    """Retrieves a payment by its ID with proper authorization.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200.
    """
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("superadmin")
    response = client.get(f"/payments/{payment_id}", headers=headers)
    assert response.status_code == 200


def test_get_payment_by_id_no_auth(client_with_token):
    """Attempts to retrieve a payment by ID without sufficient authorization.

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
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("user")
    response = client.get(f"/payments/{payment_id}", headers=headers)
    assert response.status_code == 403


def test_get_nonexisting_payment(client_with_token):
    """Attempts to retrieve a non-existing payment by ID.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/1000", headers=headers)
    assert response.status_code == 404


def test_get_payment_id_not_int(client_with_token):
    """Attempts to retrieve a payment using a non-integer payment ID.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 422.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/hallo", headers=headers)
    assert response.status_code == 422


def test_get_payments_by_id_no_header(client):
    """Attempts to retrieve a payment by ID without authentication headers.

    Args:
        client: Unauthenticated test client.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
    response = client.get("/payments/1")
    assert response.status_code == 401


# /payments/me
def test_get_my_payments(client_with_token):
    """Retrieves payments for the authenticated user.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/me", headers=headers)
    assert response.status_code == 200


def test_get_my_payments_empty(client_with_token):
    """Attempts to retrieve payments for a user with no payments.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    client, headers = client_with_token("lotadmin")
    response = client.get("/payments/me", headers=headers)
    assert response.status_code == 404


def test_get_my_payments_no_header(client):
    """Attempts to retrieve user payments without authentication.

    Args:
        client: Unauthenticated test client.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
    response = client.get("/payments/me")
    assert response.status_code == 401


# /payments/me/open
def test_get_my_open_payments(client_with_token):
    """Retrieves open payments for the authenticated user.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/me/open", headers=headers)
    assert response.status_code == 200


def test_get_my_open_payments_empty(client_with_token):
    """Attempts to retrieve open payments for a user with no open payments.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    client, headers = client_with_token("lotadmin")
    response = client.get("/payments/me/open", headers=headers)
    assert response.status_code == 404


def test_get_my_open_payments_no_header(client):
    """Attempts to retrieve open payments without authentication.

    Args:
        client: Unauthenticated test client.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
    response = client.get("/payments/me/open")
    assert response.status_code == 401


# /payments/user/{user_id}
def test_get_payments_by_user_id(client_with_token):
    """Retrieves payments for a specific user by user ID.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/user/1", headers=headers)
    assert response.status_code == 200


def test_get_payments_by_user_id_not_int(client_with_token):
    """Attempts to retrieve payments using a non-integer user ID.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 422.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/user/hallo", headers=headers)
    assert response.status_code == 422


def test_get_payments_by_user_id_no_authorization(client_with_token):
    """Attempts to retrieve payments for a user without sufficient permissions.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 403.
    """
    client, headers = client_with_token("user")
    response = client.get("/payments/user/1", headers=headers)
    assert response.status_code == 403


def test_get_payments_by_user_id_empty(client_with_token):
    """Attempts to retrieve payments for a user with no payments.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/user/4", headers=headers)
    assert response.status_code == 404


def test_get_payments_by_user_id_nonexistent_user(client_with_token):
    """Attempts to retrieve payments for a non-existing user.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/user/1000", headers=headers)
    assert response.status_code == 404


def test_get_payments_by_user_id_no_header(client):
    """Attempts to retrieve payments for a user without authentication.

    Args:
        client: Unauthenticated test client.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
    response = client.get("/payments/user/1")
    assert response.status_code == 401


# /payments/user/{user_id}/open
def test_get_open_payments_by_user_id(client_with_token):
    """Retrieves open payments for a specific user by user ID.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/user/1/open", headers=headers)
    assert response.status_code == 200


def test_get_open_payments_by_user_id_not_int(client_with_token):
    """Attempts to retrieve open payments using a non-integer user ID.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 422.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/user/hallo", headers=headers)
    assert response.status_code == 422


def test_get_open_payments_by_user_id_no_authorization(client_with_token):
    """Attempts to retrieve open payments for a user without sufficient permissions.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 403.
    """
    client, headers = client_with_token("user")
    response = client.get("/payments/user/1/open", headers=headers)
    assert response.status_code == 403


def test_get_open_payments_by_user_id_empty(client_with_token):
    """Attempts to retrieve open payments for a user with no open payments.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/user/4/open", headers=headers)
    assert response.status_code == 404


def test_get_open_payments_by_user_id_nonexistent_user(client_with_token):
    """Attempts to retrieve open payments for a non-existing user.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/user/1000/open", headers=headers)
    assert response.status_code == 404


def test_get_open_payments_by_user_id_no_header(client):
    """Attempts to retrieve open payments without authentication.

    Args:
        client: Unauthenticated test client.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
    response = client.get("/payments/user/1/open")
    assert response.status_code == 401


# /payments/refunds
def test_get_refunds_empty(client_with_token):
    """Attempts to retrieve refunds when no refunds exist.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/refunds", headers=headers)
    assert response.status_code == 404


def test_get_refunds_empty_with_user(client_with_token):
    """Attempts to retrieve refunds for a specific user when no refunds exist.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/refunds?user_id=1", headers=headers)
    assert response.status_code == 404
