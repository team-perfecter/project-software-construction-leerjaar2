from unittest.mock import patch
from fastapi.testclient import TestClient
from api.tests.conftest import get_last_discount_code
from api.main import app

client = TestClient(app)


def test_update_discount_code_with_superadmin(client_with_token):
    client, headers = client_with_token("superadmin")
    code = get_last_discount_code(client_with_token)
    fake_code = {
        "code": "code1",
        "discount_type": "percentage",
        "discount_value": 5
    }
    response = client.put(f"/discount-codes/{code}",
                          json=fake_code, headers=headers)
    assert response.status_code == 200


def test_update_discount_code_nonexistent(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_code = {
        "code": "code1",
        "discount_type": "percentage",
        "discount_value": 5
    }
    response = client.put(f"/discount-codes/fakecode",
                          json=fake_code, headers=headers)
    assert response.status_code == 404


@patch("api.models.discount_code_model.DiscountCodeModel.update_discount_code",
       return_value=False)
def test_update_discount_code_server_error(mock_create, client_with_token):
    client, headers = client_with_token("superadmin")
    code = get_last_discount_code(client_with_token)
    fake_code = {
        "code": "1",
        "discount_type": "percentage",
        "discount_value": 5
    }
    response = client.put(f"/discount-codes/{code}",
                          json=fake_code, headers=headers)
    assert response.status_code == 500


def test_update_discount_code_without_authorisation(client_with_token):
    client, headers = client_with_token("user")
    code = get_last_discount_code(client_with_token)
    fake_code = {
        "code": "1",
        "discount_type": "percentage",
        "discount_value": 5
    }
    response = client.put(f"/discount-codes/{code}",
                          json=fake_code, headers=headers)
    assert response.status_code == 403


def test_update_discount_code_no_token(client):
    fake_code = {
        "code": "1",
        "discount_type": "percentage",
        "discount_value": 5
    }
    response = client.put("/discount-codes/fakecode",
                          json=fake_code)
    assert response.status_code == 401


def test_update_discount_code_wrong_data_type(client_with_token):
    client, headers = client_with_token("superadmin")
    code = get_last_discount_code(client_with_token)
    fake_code = {
        "code": 32423,
        "discount_type": "percentage",
        "discount_value": 5
    }
    response = client.put(f"/discount-codes/{code}",
                          json=fake_code, headers=headers)
    assert response.status_code == 422


def test_update_discount_code_duplicate_code(client_with_token):
    client, headers = client_with_token("superadmin")
    code = get_last_discount_code(client_with_token)
    fake_code = {
        "code": "test1",
        "discount_type": "percentage",
        "discount_value": 5
    }
    response = client.put(f"/discount-codes/{code}",
                          json=fake_code, headers=headers)
    assert response.status_code == 409


def test_update_discount_code_invalid_discount_type(client_with_token):
    client, headers = client_with_token("superadmin")
    code = get_last_discount_code(client_with_token)
    fake_code = {
        "code": "2",
        "discount_type": "blabla",
        "discount_value": 5
    }
    response = client.put(f"/discount-codes/{code}",
                          json=fake_code, headers=headers)
    assert response.status_code == 400


def test_update_discount_code_invalid_discount_value(client_with_token):
    client, headers = client_with_token("superadmin")
    code = get_last_discount_code(client_with_token)
    fake_code = {
        "code": "2",
        "discount_type": "percentage",
        "discount_value": -5
    }
    response = client.put(f"/discount-codes/{code}",
                          json=fake_code, headers=headers)
    assert response.status_code == 400


def test_update_discount_code_invalid_minimum_price(client_with_token):
    client, headers = client_with_token("superadmin")
    code = get_last_discount_code(client_with_token)
    fake_code = {
        "code": "2",
        "discount_type": "percentage",
        "discount_value": 5,
        "minimum_price": -5
    }
    response = client.put(f"/discount-codes/{code}",
                          json=fake_code, headers=headers)
    assert response.status_code == 400


def test_update_discount_code_invalid_use_amount(client_with_token):
    client, headers = client_with_token("superadmin")
    code = get_last_discount_code(client_with_token)
    fake_code = {
        "code": "2",
        "discount_type": "percentage",
        "discount_value": 5,
        "use_amount": -5
    }
    response = client.put(f"/discount-codes/{code}",
                          json=fake_code, headers=headers)
    assert response.status_code == 400


def test_update_discount_code_missing_applicable_time(client_with_token):
    client, headers = client_with_token("superadmin")
    code = get_last_discount_code(client_with_token)
    fake_code = {
        "code": "2",
        "discount_type": "percentage",
        "discount_value": 5,
        "start_applicable_time": "00:01:00"
    }
    response = client.put(f"/discount-codes/{code}",
                          json=fake_code, headers=headers)
    assert response.status_code == 400


def test_update_discount_code_invalid_applicable_time(client_with_token):
    client, headers = client_with_token("superadmin")
    code = get_last_discount_code(client_with_token)
    fake_code = {
        "code": "2",
        "discount_type": "percentage",
        "discount_value": 5,
        "start_applicable_time": "12:00:00",
        "end_applicable_time": "10:00:00"
    }
    response = client.put(f"/discount-codes/{code}",
                          json=fake_code, headers=headers)
    assert response.status_code == 400


def test_update_discount_code_invalid_end_with_current_date(client_with_token):
    client, headers = client_with_token("superadmin")
    code = get_last_discount_code(client_with_token)
    fake_code = {
        "code": "2",
        "discount_type": "percentage",
        "discount_value": 5,
        "end_date": "2022-01-01"
    }
    response = client.put(f"/discount-codes/{code}",
                          json=fake_code, headers=headers)
    assert response.status_code == 400


def test_update_discount_code_invalid_start_with_end_date(client_with_token):
    client, headers = client_with_token("superadmin")
    code = get_last_discount_code(client_with_token)
    fake_code = {
        "code": "2",
        "discount_type": "percentage",
        "discount_value": 5,
        "start_date": "2027-01-01",
        "end_date": "2026-12-01"
    }
    response = client.put(f"/discount-codes/{code}",
                          json=fake_code, headers=headers)
    assert response.status_code == 400


# post discount-codes/{code}/deactivate
@patch(
 "api.models.discount_code_model.DiscountCodeModel.deactivate_discount_code",
 return_value=False
)
def test_deactivate_discount_code_server_error(mock_create, client_with_token):
    discount_code = get_last_discount_code(client_with_token)
    client, headers = client_with_token("superadmin")
    response = client.post(f"/discount-codes/{discount_code}/deactivate",
                           json={},
                           headers=headers)
    assert response.status_code == 500


def test_deactivate_discount_code(client_with_token):
    discount_code = get_last_discount_code(client_with_token)
    client, headers = client_with_token("superadmin")
    response = client.post(f"discount-codes/{discount_code}/deactivate",
                           json={}, headers=headers)
    assert response.status_code == 200


def test_deactivate_discount_code_no_auth(client):
    response = client.post("discount-codes/fakecode/deactivate",
                           json={})
    assert response.status_code == 401


def test_deactivate_discount_code_already_deactivated(client_with_token):
    discount_code = get_last_discount_code(client_with_token)
    client, headers = client_with_token("superadmin")
    response = client.post(f"discount-codes/{discount_code}/deactivate",
                           json={},
                           headers=headers)
    assert response.status_code == 200
    response = client.post(f"discount-codes/{discount_code}/deactivate",
                           json={},
                           headers=headers)
    assert response.status_code == 400


def test_deactivate_nonexistent_discount_code(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.post("discount-codes/fakecode/deactivate",
                           json={}, headers=headers)
    assert response.status_code == 404


def test_deactivate_discount_code_no_header(client):
    fake_discount_code = {}
    response = client.post("discount-codes/1/deactivate",
                           json=fake_discount_code)
    assert response.status_code == 401
