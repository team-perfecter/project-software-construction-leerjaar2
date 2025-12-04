import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.tests.conftest import get_last_pid


'''
PUT /parking-lots/{lid} endpoint tests

Each endpoint will check if the token is valid. If not valid, return 401
The validity of a token is checked in the get_user(token: str = Depends(oauth2_scheme)) function.

update_parking_lot(lid: str, data: dict) updates the parking lot with the given parking lot id. 
This happens with the function db_update_parking_lot(id: str, data: dict)

update_parking_lot returns status code 200 (updated) or 404 (not found) or 403 (access denied)
Only admin users can update parking lots.
'''

client = TestClient(app)

@pytest.fixture
def valid_parking_lot_data():
    return {
        "name": "Bedrijventerrein Almere Parkeergarage",
        "location": "Industrial Zone",
        "address": "Schanssingel 337, 2421 BS Almere",
        "capacity": 1,
        "tariff": 0.5,
        "daytariff": 0.5,
        "lat": 0,
        "lng": 0
    }

# Tests voor PUT /parking-lots/{id}
def test_update_parking_lot_success(client_with_token, valid_parking_lot_data):
    """Test: PUT /parking-lots/{id} - Succesvol updaten parking lot"""
    client, headers = client_with_token("superadmin")
    parking_lot_id = get_last_pid(client)
    response = client.put(f"/parking-lots/{parking_lot_id}", headers=headers, json=valid_parking_lot_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)

def test_update_parking_lot_not_found(client_with_token, valid_parking_lot_data):
    """Test: PUT /parking-lots/{id} - Niet bestaande parking lot"""
    client, headers = client_with_token("superadmin")
    response = client.put(f"/parking-lots/999999", headers=headers, json=valid_parking_lot_data)
    assert response.status_code == 404

def test_update_parking_lot_unauthorized(client_with_token, valid_parking_lot_data):
    """Test: PUT /parking-lots/{id} - Zonder authenticatie"""
    parking_lot_id = get_last_pid(client)
    response = client.put(f"/parking-lots/{parking_lot_id}", json=valid_parking_lot_data)
    assert response.status_code == 401

def test_update_parking_lot_forbidden(client_with_token, valid_parking_lot_data):
    """Test: PUT /parking-lots/{id} - Normale user toegang geweigerd"""
    client, headers = client_with_token("admin")
    parking_lot_id = get_last_pid(client)
    response = client.put(f"/parking-lots/{parking_lot_id}", headers=headers, json=valid_parking_lot_data)
    assert response.status_code == 403

def test_update_parking_lot_invalid_data(client_with_token):
    """Test: PUT /parking-lots/{id} - Ongeldige data"""
    client, headers = client_with_token("superadmin")
    parking_lot_id = get_last_pid(client)
    invalid_data = {
        "capacity": "invalid_number",  # Should be integer
        "tariff": -5.0,  # Negative tariff
        "name": ""  # Empty name
    }
    response = client.put(f"/parking-lots/{parking_lot_id}", headers=headers, json=invalid_data)
    assert response.status_code in [400, 422]