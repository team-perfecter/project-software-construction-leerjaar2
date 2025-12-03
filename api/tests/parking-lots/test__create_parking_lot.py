from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_create_parking_lot_with_superadmin(client_with_token):
    """Test: POST /parking-lots - Succesvol aanmaken parking lot"""
    client, headers = client_with_token("superadmin")
    fake_parking_lot = {
        "name": "test",
        "location": "here",
        "address": "",
        "capacity": 1,
        "tariff": 0.5,
        "daytariff": 0.5,
        "lat": 0,
        "lng": 0
    }
    response = client.post("/parking-lots", json=fake_parking_lot, headers=headers)
    assert response.status_code == 201

def test_create_parking_lot_with_admin(client_with_token):
    client, headers = client_with_token("admin")
    fake_parking_lot = {
        "name": "test",
        "location": "here",
        "address": "",
        "capacity": 1,
        "tariff": 0.5,
        "daytariff": 0.5,
        "lat": 0,
        "lng": 0
    }
    response = client.post("/parking-lots", json=fake_parking_lot, headers=headers)
    assert response.status_code == 401

def test_create_parking_lot_with_user(client_with_token):
    client, headers = client_with_token("user")
    fake_parking_lot = {
        "name": "test",
        "location": "here",
        "address": "",
        "capacity": 1,
        "tariff": 0.5,
        "daytariff": 0.5,
        "lat": 0,
        "lng": 0
    }
    response = client.post("/parking-lots", json=fake_parking_lot, headers=headers)
    assert response.status_code == 401


def test_create_parking_lot_invalid_data(client_with_token):
    client, headers = client_with_token("superadmin")
    """Test: POST /parking-lots - Ongeldige data"""
    invalid_data = "this should be invalid data"
    response = client.post("/parking-lots", json=invalid_data, headers=headers)
    assert response.status_code in [400, 422]

def test_create_parking_lot_missing_required_fields(client_with_token):
    """Test: POST /parking-lots - Missende verplichte velden"""
    client, headers = client_with_token("superadmin")
    incomplete_data = {
        "name": "Test Parking"
        # Missing location, capacity, etc.
    }
    response = client.post("/parking-lots", json=incomplete_data, headers=headers)
    assert response.status_code in [400, 422]