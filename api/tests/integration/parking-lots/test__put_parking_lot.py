from datetime import datetime

import pytest
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

@pytest.fixture
def valid_parking_lot_data():
    """
    Returns a valid parking lot.
    """
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
    superadmin_client, headers = client_with_token("superadmin")
    parking_lot_id = get_last_pid(superadmin_client)
    response = superadmin_client.put(f"/parking-lots/{parking_lot_id}", headers=headers, json=valid_parking_lot_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)

def test_update_parking_lot_not_found(client_with_token, valid_parking_lot_data):
    """Test: PUT /parking-lots/{id} - Niet bestaande parking lot"""
    superadmin_client, headers = client_with_token("superadmin")
    response = superadmin_client.put(f"/parking-lots/999999", headers=headers, json=valid_parking_lot_data)
    assert response.status_code == 404

def test_update_parking_lot_unauthorized(client, valid_parking_lot_data):
    """Test: PUT /parking-lots/{id} - Zonder authenticatie"""
    parking_lot_id = get_last_pid(client)
    response = client.put(f"/parking-lots/{parking_lot_id}", json=valid_parking_lot_data)
    assert response.status_code == 401

def test_update_parking_lot_forbidden(client_with_token, valid_parking_lot_data):
    """Test: PUT /parking-lots/{id} - Normale user toegang geweigerd"""
    admin_client, headers = client_with_token("lotadmin")
    parking_lot_id = get_last_pid(admin_client)
    response = admin_client.put(f"/parking-lots/{parking_lot_id}", headers=headers, json=valid_parking_lot_data)
    assert response.status_code == 403

def test_update_parking_lot_invalid_data(client_with_token):
    """Test: PUT /parking-lots/{id} - Ongeldige data"""
    superadmin_client, headers = client_with_token("superadmin")
    parking_lot_id = get_last_pid(superadmin_client)
    invalid_data = {
        "capacity": "invalid_number",  # Should be integer
        "tariff": -5.0,  # Negative tariff
        "name": ""  # Empty name
    }
    response = superadmin_client.put(f"/parking-lots/{parking_lot_id}", headers=headers, json=invalid_data)
    assert response.status_code in [400, 422]


def test_update_parking_lot_status_success(client_with_token):
    superadmin_client, headers = client_with_token("superadmin")
    pid = get_last_pid(superadmin_client)
    data = {
        "lid": pid,
        "lot_status": "closed",
        "closed_reason": "for testing",
        "closed_date": datetime.now().strftime("%Y-%m-%d")
    }
    response = superadmin_client.put(f"/parking-lots/{pid}/status", headers=headers, params=data)
    assert response.status_code == 200
    assert response.json()["new_status"] == "closed"

def test_update_parking_lot_status_forbidden(client_with_token):
    user_client, headers = client_with_token("user")
    pid = get_last_pid(user_client)
    data = {
        "lid": pid,
        "lot_status": "closed",
        "closed_reason": "for testing",
        "closed_date": datetime.now().strftime("%Y-%m-%d")
    }
    response = user_client.put(f"/parking-lots/{pid}/status", headers=headers, params=data)
    assert response.status_code == 403

def test_update_parking_lot_status_unaothorized(client):
    pid = get_last_pid(client)
    data = {
        "lid": pid,
        "lot_status": "closed",
        "closed_reason": "for testing",
        "closed_date": datetime.now().strftime("%Y-%m-%d")
    }
    response = client.put(f"/parking-lots/{pid}/status", params=data)
    assert response.status_code == 401

def test_update_parking_lot_status_invalid_status(client_with_token):
    superadmin_client, headers = client_with_token("superadmin")
    pid = get_last_pid(superadmin_client)
    data = {
        "lid": pid,
        "lot_status": "invalid",
        "closed_reason": "for testing",
        "closed_date": datetime.now().strftime("%Y-%m-%d")
    }
    response = superadmin_client.put(f"/parking-lots/{pid}/status", headers=headers, params=data)
    assert response.status_code == 400

def test_update_parking_lot_status_no_closed_reason(client_with_token):
    superadmin_client, headers = client_with_token("superadmin")
    pid = get_last_pid(superadmin_client)
    data = {
        "lid": pid,
        "lot_status": "closed",
        "closed_date": datetime.now().strftime("%Y-%m-%d")
    }
    response = superadmin_client.put(f"/parking-lots/{pid}/status", headers=headers, params=data)
    assert response.status_code == 400

def test_update_parking_lot_status_no_closed_date(client_with_token):
    superadmin_client, headers = client_with_token("superadmin")
    pid = get_last_pid(superadmin_client)
    data = {
        "lid": pid,
        "lot_status": "closed",
        "closed_reason": "for testing",
    }
    response = superadmin_client.put(f"/parking-lots/{pid}/status", headers=headers, params=data)
    assert response.status_code == 200
    assert response.json()["new_status"] == "closed"

def test_update_parking_lot_increase_reserved_count_success(client_with_token):
    superadmin_client, headers = client_with_token("superadmin")
    lid = get_last_pid(superadmin_client)
    response = superadmin_client.get(f"/parking-lots/{lid}")
    current_reserved = response.json()["reserved"]

    data = {
        "lid": lid,
        "action": "increase"
    }
    _ = superadmin_client.put(f"/parking-lots/{lid}/reserved", headers=headers, params=data)
    assert response.status_code == 200
    response = superadmin_client.get(f"/parking-lots/{lid}")
    assert response.json()["reserved"] == current_reserved + 1

    data = {
        "lid": lid,
        "action": "decrease"
    }
    _ = superadmin_client.put(f"/parking-lots/{lid}/reserved", headers=headers, params=data)
    assert response.status_code == 200
    response = superadmin_client.get(f"/parking-lots/{lid}")
    assert response.json()["reserved"] == current_reserved

