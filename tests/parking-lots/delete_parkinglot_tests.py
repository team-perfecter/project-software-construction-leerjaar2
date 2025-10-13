from unittest.mock import patch
from datetime import datetime, timedelta
import pytest
import jwt
from fastapi.testclient import TestClient
from ../../app import app

'''
DELETE /parking-lots/{lid} endpoint tests

Each endpoint will check if the token is valid. If not valid, return 401
The validity of a token is checked in the get_user(token: str = Depends(oauth2_scheme)) function.

delete_parking_lot(lid: str) deletes the parking lot with the given parking lot id. 
This happens with the function db_delete_parking_lot(id: str)

delete_parking_lot returns status code 200 (deleted) or 404 (not found) or 403 (access denied)
Only admin users can delete parking lots.
'''

client = TestClient(app)

# Secret key en algorithm voor token creation
SECRET_KEY = "test-secret-key"
ALGORITHM = "HS256"

def create_test_token(username: str, role: str = "USER"):
    expire = datetime.utcnow() + timedelta(minutes=30)
    token = jwt.encode({"sub": username, "exp": expire, "role": role}, SECRET_KEY, algorithm=ALGORITHM)
    return token

@pytest.fixture
def valid_admin_token():
    return create_test_token("admin", role="ADMIN")

@pytest.fixture
def valid_user_token():
    return create_test_token("testuser", role="USER")

@pytest.fixture
def valid_admin_headers(valid_admin_token):
    return {"Authorization": f"Bearer {valid_admin_token}"}

@pytest.fixture
def valid_user_headers(valid_user_token):
    return {"Authorization": f"Bearer {valid_user_token}"}

@pytest.fixture
def invalid_headers():
    return {"Authorization": "Bearer invalid"}

def get_fake_parking_lots():
    return {
        "1": {
            "id": "1",
            "name": "Bedrijventerrein Almere Parkeergarage",
            "location": "Industrial Zone",
            "address": "Schanssingel 337, 2421 BS Almere",
            "capacity": 335,
            "reserved": 77,
            "tariff": 1.9,
            "daytariff": 11,
            "created_at": "2020-03-25",
            "coordinates": {
                "lat": 52.3133,
                "lng": 5.2234
            }
        },
        "2": {
            "id": "2",
            "name": "Vlaardingen Evenementenhal Parkeerterrein",
            "location": "Event Center",
            "address": "Westlindepark 756, 8920 AB Vlaardingen",
            "capacity": 730,
            "reserved": 136,
            "tariff": 3.2,
            "daytariff": 16,
            "created_at": "2019-02-25",
            "coordinates": {
                "lat": 51.8921,
                "lng": 4.3731
            }
        }
    }

def delete_fake_parking_lot(lid: str):
    """Simuleer het verwijderen van een parking lot"""
    if lid in ["1", "2"]:  # Geldige IDs
        return True
    return False

# Tests voor DELETE /parking-lots/{id}
@patch("path.to.function.db_delete_parking_lot", side_effect=delete_fake_parking_lot)
def test_delete_parking_lot_success(mock_db, valid_admin_headers):
    """Test: DELETE /parking-lots/{id} - Succesvol verwijderen parking lot"""
    parking_lot_id = "1"
    response = client.delete(f"/parking-lots/{parking_lot_id}", headers=valid_admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)

@patch("path.to.function.db_delete_parking_lot", return_value=False)
def test_delete_parking_lot_not_found(mock_db, valid_admin_headers):
    """Test: DELETE /parking-lots/{id} - Niet bestaande parking lot"""
    invalid_id = "999999"
    response = client.delete(f"/parking-lots/{invalid_id}", headers=valid_admin_headers)
    assert response.status_code == 404

@patch("path.to.function.db_delete_parking_lot", side_effect=delete_fake_parking_lot)
def test_delete_parking_lot_unauthorized(mock_db):
    """Test: DELETE /parking-lots/{id} - Zonder authenticatie"""
    parking_lot_id = "1"
    response = client.delete(f"/parking-lots/{parking_lot_id}")
    assert response.status_code == 401

@patch("path.to.function.db_delete_parking_lot", side_effect=delete_fake_parking_lot)
def test_delete_parking_lot_forbidden(mock_db, valid_user_headers):
    """Test: DELETE /parking-lots/{id} - Normale user toegang geweigerd"""
    parking_lot_id = "1"
    response = client.delete(f"/parking-lots/{parking_lot_id}", headers=valid_user_headers)
    assert response.status_code == 403

@patch("path.to.function.db_delete_parking_lot", return_value=False)
def test_delete_parking_lot_invalid_id(mock_db, valid_admin_headers):
    """Test: DELETE /parking-lots/{id} - Ongeldige ID format"""
    invalid_id = "abc"
    response = client.delete(f"/parking-lots/{invalid_id}", headers=valid_admin_headers)
    assert response.status_code in [400, 404, 422]