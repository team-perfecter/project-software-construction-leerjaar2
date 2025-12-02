from unittest.mock import patch
from datetime import datetime, timedelta
import pytest
import jwt
from fastapi.testclient import TestClient
from api.main import app

'''
POST /parking-lots endpoint tests

Each endpoint will check if the token is valid. If not valid, return 401
The validity of a token is checked in the get_user(token: str = Depends(oauth2_scheme)) function.

create_parking_lot(data: dict) creates a new parking lot with the given data. 
This happens with the function db_create_parking_lot(data: dict)

create_parking_lot returns status code 201 (created) or 400 (invalid data) or 403 (access denied)
Only admin users can create parking lots.
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

@pytest.fixture
def valid_parking_lot_data():
    return {
        "name": "Test Parking Lot",
        "location": "Test Location",
        "address": "Test Address 123, 1234 AB TestCity",
        "capacity": 100,
        "tariff": 2.5,
        "daytariff": 15.0,
        "coordinates": {
            "lat": 52.3676,
            "lng": 4.9041
        }
    }

def create_fake_parking_lot(data: dict):
    """Simuleer het aanmaken van een parking lot"""
    if "name" in data and "location" in data and "capacity" in data:
        return {
            "id": "1500",
            "name": data["name"],
            "location": data["location"],
            "address": data.get("address", "Unknown Address"),
            "capacity": data["capacity"],
            "reserved": 0,
            "tariff": data.get("tariff", 2.0),
            "daytariff": data.get("daytariff", 15.0),
            "created_at": "2024-01-01",
            "coordinates": data.get("coordinates", {"lat": 0.0, "lng": 0.0})
        }
    return None

# Tests voor POST /parking-lots
@patch("path.to.function.db_create_parking_lot", side_effect=create_fake_parking_lot)
def test_create_parking_lot_success(mock_db, valid_admin_headers, valid_parking_lot_data):
    """Test: POST /parking-lots - Succesvol aanmaken parking lot"""
    response = client.post("/parking-lots", headers=valid_admin_headers, json=valid_parking_lot_data)
    assert response.status_code == 201
    data = response.json()
    assert isinstance(data, dict)

@patch("path.to.function.db_create_parking_lot", return_value=None)
def test_create_parking_lot_unauthorized(mock_db, valid_parking_lot_data):
    """Test: POST /parking-lots - Zonder authenticatie"""
    response = client.post("/parking-lots", json=valid_parking_lot_data)
    assert response.status_code == 401

@patch("path.to.function.db_create_parking_lot", side_effect=create_fake_parking_lot)
def test_create_parking_lot_forbidden(mock_db, valid_user_headers, valid_parking_lot_data):
    """Test: POST /parking-lots - Normale user toegang geweigerd"""
    response = client.post("/parking-lots", headers=valid_user_headers, json=valid_parking_lot_data)
    assert response.status_code == 403

@patch("path.to.function.db_create_parking_lot", return_value=None)
def test_create_parking_lot_invalid_data(mock_db, valid_admin_headers):
    """Test: POST /parking-lots - Ongeldige data"""
    invalid_data = {
        "name": "",  # Empty name
        "capacity": -10,  # Negative capacity
        "tariff": "invalid"  # Invalid tariff type
    }
    response = client.post("/parking-lots", headers=valid_admin_headers, json=invalid_data)
    assert response.status_code in [400, 422]

@patch("path.to.function.db_create_parking_lot", return_value=None)
def test_create_parking_lot_missing_required_fields(mock_db, valid_admin_headers):
    """Test: POST /parking-lots - Missende verplichte velden"""
    incomplete_data = {
        "name": "Test Parking"
        # Missing location, capacity, etc.
    }
    response = client.post("/parking-lots", headers=valid_admin_headers, json=incomplete_data)
    assert response.status_code in [400, 422]