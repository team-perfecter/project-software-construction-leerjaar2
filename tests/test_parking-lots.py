import pytest
import requests
import json

BASE_URL = "http://localhost:8000"

class TestParkingLots:
    """Test parking lot endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Login als admin en geef token terug"""
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        return response.json()["session_token"]
    
    @pytest.fixture
    def user_token(self):
        """Login als normale user en geef token terug"""
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        return response.json()["session_token"]

# GET /parking-lots
# POST /parking-lots
# GET /parking-lots/{id}
    def test_get_parking_lot_by_id(self, admin_token):
        """Test ophalen van specifieke parking lot"""
        # Eerst een parking lot aanmaken
        parking_lot_data = {
            "name": "Test Parking Lot",
            "location": "Test Street 123",
            "capacity": 100,
            "tariff": "2.50",
            "daytariff": "15.00"
        }
        
        # Maak parking lot aan
        create_response = requests.post(
            f"{BASE_URL}/parking-lots",
            json=parking_lot_data,
            headers={"Authorization": admin_token}
        )
        assert create_response.status_code == 201
        
        # Extract ID uit response (aangenomen dat server ID teruggeeft)
        created_id = "1"  # Of parse uit create_response.text
        
        # Test GET /parking-lots/{id}
        response = requests.get(f"{BASE_URL}/parking-lots/{created_id}")
        
        # Verificaties
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Parking Lot"
        assert data["location"] == "Test Street 123"
        assert data["capacity"] == 100
        assert data["tariff"] == "2.50"
        assert data["daytariff"] == "15.00"

    def test_get_nonexistent_parking_lot(self):
        """Test ophalen van niet-bestaande parking lot"""
        response = requests.get(f"{BASE_URL}/parking-lots/999")
        assert response.status_code == 404
        assert b"Parking lot not found" in response.content
# GET /parking-lots/availability
# GET /parking-lots/{id}/availability

# PUT/PATCH /parking-lots/{id} (Update)
# DELETE /parking-lots/{id} (Delete)
# GET /parking-lots/search (Search)
# GET /parking-lots/{id}/reservations (Reservations per lot)
# GET /parking-lots/{id}/stats (Statistics)
# POST /parking-lots/{id}/maintenance (Maintenance mode)
# GET /parking-lots/nearby (Location-based search)
