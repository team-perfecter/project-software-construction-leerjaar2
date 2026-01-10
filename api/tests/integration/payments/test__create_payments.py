from unittest.mock import patch
from fastapi.testclient import TestClient
from api.main import app
from api.tests.conftest import get_last_pid

client = TestClient(app)


def test_create_payment_with_superadmin(client_with_token):
    client, headers = client_with_token("superadmin")
    lot2 = {
            "name": "Vlaardingen Evenementenhal Parkeerterrein",
            "location": "Event Center",
            "address": "Westlindepark 756, 8920 AB Vlaardingen",
            "capacity": 50,
            "tariff": 0.5,
            "daytariff": 0.5,
            "lat": 0,
            "lng": 0
        }

    client.post("/parking-lots", json=lot2, headers=headers)
    pid = get_last_pid(client)
    fake_payment = {
        "user_id": 1,
        "parking_lot_id": pid,
        "amount": 200,
        "method": "method1"
    }
    response = client.post("/payments", json=fake_payment, headers=headers)
    assert response.status_code == 201


def test_create_payment_with_paymentadmin(client_with_token):
    client, headers = client_with_token("superadmin")
    lot2 = {
            "name": "Vlaardingen Evenementenhal Parkeerterrein",
            "location": "Event Center",
            "address": "Westlindepark 756, 8920 AB Vlaardingen",
            "capacity": 50,
            "tariff": 0.5,
            "daytariff": 0.5,
            "lat": 0,
            "lng": 0
        }

    client.post("/parking-lots", json=lot2, headers=headers)
    client, headers = client_with_token("paymentadmin")
    pid = get_last_pid(client)
    fake_payment = {
        "user_id": 1,
        "parking_lot_id": pid,
        "amount": 100,
        "method": "method2"
    }
    response = client.post("/payments", json=fake_payment, headers=headers)
    assert response.status_code == 201


@patch("api.models.payment_model.PaymentModel.create_payment",
       return_value=False)
def test_create_payment_server_error(mock_create, client_with_token):
    client, headers = client_with_token("superadmin")
    lot2 = {
            "name": "Vlaardingen Evenementenhal Parkeerterrein",
            "location": "Event Center",
            "address": "Westlindepark 756, 8920 AB Vlaardingen",
            "capacity": 50,
            "tariff": 0.5,
            "daytariff": 0.5,
            "lat": 0,
            "lng": 0
        }

    client.post("/parking-lots", json=lot2, headers=headers)
    pid = get_last_pid(client)
    fake_payment = {
        "user_id": 1,
        "parking_lot_id": pid,
        "amount": 200,
        "method": "method1"
    }
    response = client.post("/payments", json=fake_payment, headers=headers)
    assert response.status_code == 500


def test_create_payment_without_authorization(client_with_token):
    client, headers = client_with_token("superadmin")
    lot2 = {
            "name": "Vlaardingen Evenementenhal Parkeerterrein",
            "location": "Event Center",
            "address": "Westlindepark 756, 8920 AB Vlaardingen",
            "capacity": 50,
            "tariff": 0.5,
            "daytariff": 0.5,
            "lat": 0,
            "lng": 0
        }

    client.post("/parking-lots", json=lot2, headers=headers)
    client, headers = client_with_token("user")
    pid = get_last_pid(client)
    fake_payment = {
        "user_id": 1,
        "parking_lot_id": pid,
        "amount": 100,
        "method": "method3"
    }
    response = client.post("/payments", json=fake_payment, headers=headers)
    assert response.status_code == 403


def test_create_payment_no_token(client):
    fake_payment = {
        "user_id": 1,
        "parking_lot_id": 1,
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
    lot2 = {
            "name": "Vlaardingen Evenementenhal Parkeerterrein",
            "location": "Event Center",
            "address": "Westlindepark 756, 8920 AB Vlaardingen",
            "capacity": 50,
            "tariff": 0.5,
            "daytariff": 0.5,
            "lat": 0,
            "lng": 0
        }

    client.post("/parking-lots", json=lot2, headers=headers)
    pid = get_last_pid(client)
    fake_payment = {
        "user_id": 1,
        "parking_lot_id": pid,
        "amount": 1,
        "method": 123
    }
    response = client.post("/payments", json=fake_payment, headers=headers)
    assert response.status_code == 422


def test_create_payment_nonexistent_user(client_with_token):
    client, headers = client_with_token("superadmin")
    lot2 = {
            "name": "Vlaardingen Evenementenhal Parkeerterrein",
            "location": "Event Center",
            "address": "Westlindepark 756, 8920 AB Vlaardingen",
            "capacity": 50,
            "tariff": 0.5,
            "daytariff": 0.5,
            "lat": 0,
            "lng": 0
        }

    client.post("/parking-lots", json=lot2, headers=headers)
    pid = get_last_pid(client)
    fake_payment = {
        "user_id": 53478653653753,
        "parking_lot_id": pid,
        "amount": 200,
        "method": "method1"
    }
    response = client.post("/payments", json=fake_payment, headers=headers)
    assert response.status_code == 404


def test_create_payment_nonexistent_lot(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_payment = {
        "user_id": 1,
        "parking_lot_id": 353453523687,
        "amount": 200,
        "method": "method1"
    }
    response = client.post("/payments", json=fake_payment, headers=headers)
    assert response.status_code == 404
