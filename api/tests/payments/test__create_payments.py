from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_create_payment_with_superadmin(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_payment = {
        "user_id": 1,
        "amount": 200,
        "method": "method1"
    }
    response = client.post("/payments", json=fake_payment, headers=headers)
    assert response.status_code == 201

def test_create_payment_with_paymentadmin(client_with_token):
    client, headers = client_with_token("paymentadmin")
    fake_payment = {
        "user_id": 1,
        "amount": 100,
        "method": "method2"
    }
    response = client.post("/payments", json=fake_payment, headers=headers)
    assert response.status_code == 201

def test_create_payment_without_authorization(client_with_token):
    client, headers = client_with_token("user")
    fake_payment = {
        "user_id": 1,
        "amount": 100,
        "method": "method3"
    }
    response = client.post("/payments", json=fake_payment, headers=headers)
    assert response.status_code == 403

def test_create_payment_no_token(client):
    fake_payment = {
        "user_id": 1,
        "amount": 100,
        "method": "method4"
    }
    response = client.post("/payments", json=fake_payment)
    assert response.status_code == 401

def test_create_payment_missing_field(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_payment = {
        "user_id": 1,
        "method": "method5"
    }
    response = client.post("/payments", json=fake_payment, headers=headers)
    assert response.status_code == 422

def test_create_payment_wrong_data_type(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_payment = {
        "user_id": 1,
        "amount": 1,
        "method": 123
    }
    response = client.post("/payments", json=fake_payment, headers=headers)
    assert response.status_code == 422