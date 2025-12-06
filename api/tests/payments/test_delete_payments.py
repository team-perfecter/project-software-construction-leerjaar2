from fastapi.testclient import TestClient
from api.main import app
from unittest.mock import patch

client = TestClient(app)


# /payments/{payment_id}
@patch("api.models.payment_model.PaymentModel.delete_payment",
       return_value=False)
def test_delete_payment_server_error(mock_create, client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.delete("/payments/1", headers=headers)
    assert response.status_code == 500


def test_delete_payment_by_id(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.delete("/payments/1", headers=headers)
    assert response.status_code == 200

    client, headers = client_with_token("superadmin")
    response = client.get("/payments/1", headers=headers)
    assert response.status_code == 404


def test_delete_payment_by_id_not_int(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.delete("/payments/hallo", headers=headers)
    assert response.status_code == 422


def test_delete_payment_by_nonexistent_id(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.delete("/payments/1000", headers=headers)
    assert response.status_code == 404


def test_delete_payment_by_id_no_authorization(client_with_token):
    client, headers = client_with_token("user")
    response = client.delete("/payments/1", headers=headers)
    assert response.status_code == 403


def test_delete_payment_by_id_no_header(client):
    response = client.delete("/payments/1")
    assert response.status_code == 401
