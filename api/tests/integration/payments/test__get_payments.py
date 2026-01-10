from fastapi.testclient import TestClient
from api.main import app
from api.tests.conftest import get_last_payment_id

client = TestClient(app)


# /payments/{payment_id}
def test_get_payment_by_id(client_with_token):
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("superadmin")
    response = client.get(f"/payments/{payment_id}", headers=headers)
    assert response.status_code == 200


def test_get_payment_by_id_no_auth(client_with_token):
    client, headers = client_with_token("superadmin")
    payment_id = get_last_payment_id(client_with_token)
    client, headers = client_with_token("user")
    response = client.get(f"/payments/{payment_id}", headers=headers)
    assert response.status_code == 403


def test_get_nonexisting_payment(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/1000", headers=headers)
    assert response.status_code == 404


def test_get_payment_id_not_int(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/hallo", headers=headers)
    assert response.status_code == 422


def test_get_payments_by_id_no_header(client):
    response = client.get("/payments/1")
    assert response.status_code == 401


# /payments/me
def test_get_my_payments(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/me", headers=headers)
    assert response.status_code == 200


def test_get_my_payments_empty(client_with_token):
    client, headers = client_with_token("admin")
    response = client.get("/payments/me", headers=headers)
    assert response.status_code == 404


def test_get_my_payments_no_header(client):
    response = client.get("/payments/me")
    assert response.status_code == 401


# /payments/me/open
def test_get_my_open_payments(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/me/open", headers=headers)
    assert response.status_code == 200


def test_get_my_open_payments_empty(client_with_token):
    client, headers = client_with_token("admin")
    response = client.get("/payments/me/open", headers=headers)
    assert response.status_code == 404


def test_get_my_open_payments_no_header(client):
    response = client.get("/payments/me/open")
    assert response.status_code == 401


# /payments/user/{user_id}
def test_get_payments_by_user_id(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/user/1", headers=headers)
    assert response.status_code == 200


def test_get_payments_by_user_id_not_int(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/user/hallo", headers=headers)
    assert response.status_code == 422


def test_get_payments_by_user_id_no_authorization(client_with_token):
    client, headers = client_with_token("user")
    response = client.get("/payments/user/1", headers=headers)
    assert response.status_code == 403


def test_get_payments_by_user_id_empty(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/user/4", headers=headers)
    assert response.status_code == 404


def test_get_payments_by_user_id_nonexistent_user(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/user/1000", headers=headers)
    assert response.status_code == 404


def test_get_payments_by_user_id_no_header(client):
    response = client.get("/payments/user/1")
    assert response.status_code == 401


# /payments/user/{user_id}/open

def test_get_open_payments_by_user_id(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/user/1/open", headers=headers)
    assert response.status_code == 200


def test_get_open_payments_by_user_id_not_int(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/user/hallo", headers=headers)
    assert response.status_code == 422


def test_get_open_payments_by_user_id_no_authorization(client_with_token):
    client, headers = client_with_token("user")
    response = client.get("/payments/user/1/open", headers=headers)
    assert response.status_code == 403


def test_get_open_payments_by_user_id_empty(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/user/4/open", headers=headers)
    assert response.status_code == 404


def test_get_open_payments_by_user_id_nonexistent_user(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/user/1000/open", headers=headers)
    assert response.status_code == 404


def test_get_open_payments_by_user_id_no_header(client):
    response = client.get("/payments/user/1/open")
    assert response.status_code == 401


# /payments/refunds
def test_get_refunds_empty(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/refunds", headers=headers)
    assert response.status_code == 404


def test_get_refunds_empty_with_user(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/refunds?user_id=1", headers=headers)
    print(response.json)
    assert response.status_code == 404
