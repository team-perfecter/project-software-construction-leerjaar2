from fastapi.testclient import TestClient
from api.main import app
from api.tests.conftest import get_last_discount_code
from unittest.mock import patch

client = TestClient(app)


@patch("api.models.discount_code_model.DiscountCodeModel.delete_discount_code",
       return_value=None)
def test_delete_discount_code_server_error(mock_create, client_with_token):
    code = get_last_discount_code(client_with_token)
    client, headers = client_with_token("superadmin")
    response = client.delete(f"/discount-codes/{code}", headers=headers)
    assert response.status_code == 500


def test_delete_discount_code_by_code(client_with_token):
    code = get_last_discount_code(client_with_token)
    client, headers = client_with_token("superadmin")
    response = client.delete(f"/discount-codes/{code}", headers=headers)
    assert response.status_code == 200

    client, headers = client_with_token("superadmin")
    response = client.get(f"/discount-codes/{code}", headers=headers)
    assert response.status_code == 404


def test_delete_discount_code_by_code_not_found(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.delete(f"/discount-codes/fakecode", headers=headers)
    assert response.status_code == 404


def test_delete_discount_code_by_code_no_auth(client_with_token):
    code = get_last_discount_code(client_with_token)
    client, headers = client_with_token("user")
    response = client.delete(f"/discount-codes/{code}", headers=headers)
    assert response.status_code == 403


def test_delete_discount_code_by_code_no_header(client):
    response = client.delete(f"/discount-codes/fakecode")
    assert response.status_code == 401
