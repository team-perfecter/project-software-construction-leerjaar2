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
# GET /parking-lots/availability
# GET /parking-lots/{id}/availability

# PUT/PATCH /parking-lots/{id} (Update)
# DELETE /parking-lots/{id} (Delete)
# GET /parking-lots/search (Search)
# GET /parking-lots/{id}/reservations (Reservations per lot)
# GET /parking-lots/{id}/stats (Statistics)
# POST /parking-lots/{id}/maintenance (Maintenance mode)
# GET /parking-lots/nearby (Location-based search)
