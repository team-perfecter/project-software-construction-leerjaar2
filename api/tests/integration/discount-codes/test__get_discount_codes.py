from fastapi.testclient import TestClient
from api.main import app
from api.tests.conftest import get_last_discount_code

client = TestClient(app)

#get discount-codes/{code}
def test_get_discount_code_by_code(client_with_token):
    code = get_last_discount_code(client_with_token)
    client, headers = client_with_token("superadmin")
    response = client.get(f"/discount-codes/{code}", headers=headers)
    assert response.status_code == 200


def test_get_discount_code_by_code_unauthorised(client_with_token):
    code = get_last_discount_code(client_with_token)
    client, headers = client_with_token("user")
    response = client.get(f"/discount-codes/{code}", headers=headers)
    assert response.status_code == 403


def test_get_discount_code_by_code_no_header(client):
    response = client.get("/discount-codes/q")
    assert response.status_code == 401


def test_get_discount_code_by_nonexistent_code(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/discount-codes/nep", headers=headers)
    assert response.status_code == 404

#get discount-codes/
def test_get_all_discount_codes(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/discount-codes", headers=headers)
    assert response.status_code == 200


def test_get_all_discount_codes_no_auth(client_with_token):
    client, headers = client_with_token("user")
    response = client.get("/discount-codes", headers=headers)
    assert response.status_code == 403


def test_get_all_discount_codes_no_auth(client):
    response = client.get("/discount-codes")
    assert response.status_code == 401


def test_get_all_discount_codes_empty(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/discount-codes", headers=headers)

    if response.status_code == 200:
        codes = response.json().get("discount_code", [])
        for discount_code in codes:
            client.delete(f"/discount-codes/{discount_code['code']}", headers=headers)

    response = client.get("/discount-codes", headers=headers)
    assert response.status_code == 404


#get discount-codes/active
def test_get_all_active_discount_codes(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/discount-codes/active", headers=headers)
    assert response.status_code == 200


def test_get_all_active_discount_codes_no_auth(client_with_token):
    client, headers = client_with_token("user")
    response = client.get("/discount-codes/active", headers=headers)
    assert response.status_code == 403


def test_get_all_active_discount_codes_no_auth(client):
    response = client.get("/discount-codes/active")
    assert response.status_code == 401


def test_get_all_active_discount_codes_empty(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/discount-codes", headers=headers)

    if response.status_code == 200:
        codes = response.json().get("discount_code", [])
        for discount_code in codes:
            client.delete(f"/discount-codes/{discount_code['code']}", headers=headers)

    response = client.get("/discount-codes/active", headers=headers)
    assert response.status_code == 404

