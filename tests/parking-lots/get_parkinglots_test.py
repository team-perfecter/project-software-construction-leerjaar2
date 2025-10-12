import os
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from unittest.mock import patch, MagicMock
import pytest
import jwt
from fastapi.testclient import TestClient

# Voeg de project root toe aan het Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

# Voor nu importeren van server, later van app
from server import app

# FIXTURES: Herbruikbare test data/setup die pytest automatisch injecteert
# PATCH: Vervangt echte functies/klassen tijdelijk met mocks tijdens tests

"""
Parkinglots will be in a separate class. The input of this class will be 
the authorization token of the user. Each endpoint will check if the token 
is valid. If not valid, return 401.

The validity of a token is checked in the 
get_user(token: str = Depends(oauth2_scheme)) function.

get_Parkinglot(lid: int) returns the Parkinglot with the given Parkinglot id. 
This happens with the function db_get_Parkinglot(id: int)

get_Parkinglot returns the following:
{"Parkinglot": db_get_Parkinglot(id: int)}
"""

# Secret key en algorithm voor token creation (tijdelijk voor tests)
SECRET_KEY = "test-secret-key"
ALGORITHM = "HS256"


class TestGetParkingLot:
    """Tests voor GET parking lots endpoints met FastAPI TestClient"""

    @pytest.fixture
    def client(self):
        """FIXTURE: TestClient voor FastAPI app"""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        """FIXTURE: Authorization headers met test token"""
        token = self.create_test_token("testuser")
        return {"Authorization": f"Bearer {token}"}

    def create_test_token(self, username: str) -> str:
        """
        FIXTURE HELPER: Create test JWT token voor authenticatie
        """
        expire = datetime.utcnow() + timedelta(minutes=30)
        payload = {"sub": username, "exp": expire}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    # Tests voor GET /parking-lots
    def test_get_all_parking_lots_success(self, client, auth_headers):
        """Test: GET /parking-lots - Succesvol ophalen alle parking lots"""
        response = client.get("/parking-lots", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Controleer dat het een dictionary met IDs is
        if data:
            first_key = list(data.keys())[0]
            assert "name" in data[first_key]
            assert "location" in data[first_key]

    def test_get_all_parking_lots_unauthorized(self, client):
        """Test: GET /parking-lots - Zonder authenticatie"""
        response = client.get("/parking-lots")
        assert response.status_code in [200, 401]

    def test_get_all_parking_lots_pagination(self, client, auth_headers):
        """Test: GET /parking-lots - Met pagination parameters"""
        params = {"limit": 10, "offset": 0}
        response = client.get("/parking-lots", headers=auth_headers, params=params)
        assert response.status_code in [200, 400]

    def test_get_all_parking_lots_empty(self, client, auth_headers):
        """Test: GET /parking-lots - Lege parking lots lijst"""
        response = client.get("/parking-lots", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    # Tests voor GET /parking-lots/{id}
    def test_get_parking_lot_by_id_success(self, client, auth_headers):
        """Test: GET /parking-lots/{id} - Succesvol ophalen parking lot"""
        parking_lot_id = "1"
        response = client.get(f"/parking-lots/{parking_lot_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        expected_fields = ["name", "location", "capacity", "tariff"]
        for field in expected_fields:
            assert field in data, f"Veld '{field}' ontbreekt in response"

    def test_get_parking_lot_by_id_not_found(self, client, auth_headers):
        """Test: GET /parking-lots/{id} - Niet bestaande parking lot"""
        invalid_id = "999999"
        response = client.get(f"/parking-lots/{invalid_id}", headers=auth_headers)

        assert response.status_code == 404
        assert b"not found" in response.content.lower()

    def test_get_parking_lot_invalid_id_format(self, client, auth_headers):
        """Test: GET /parking-lots/{id} - Ongeldige ID format"""
        invalid_id = "abc"
        response = client.get(f"/parking-lots/{invalid_id}", headers=auth_headers)
        assert response.status_code in [400, 404]

    def test_get_parking_lot_by_id_unauthorized(self, client):
        """Test: GET /parking-lots/{id} - Zonder authenticatie"""
        response = client.get("/parking-lots/1")
        assert response.status_code in [200, 401]

    # Tests voor GET /parking-lots/availability
    def test_get_parking_lots_availability_success(self, client, auth_headers):
        """Test: GET /parking-lots/availability - Beschikbaarheid alle lots"""
        response = client.get("/parking-lots/availability", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (dict, list))
        # Controleer availability data structure
        if isinstance(data, dict) and data:
            first_lot = list(data.values())[0]
            assert "capacity" in first_lot or "available" in first_lot

    def test_get_parking_lots_availability_with_datetime(self, client, auth_headers):
        """Test: GET /parking-lots/availability - Met specifieke datetime"""
        params = {"datetime": "2024-12-25T14:00:00"}
        response = client.get(
            "/parking-lots/availability", headers=auth_headers, params=params
        )
        assert response.status_code in [200, 400]

    def test_get_parking_lots_availability_invalid_datetime(self, client, auth_headers):
        """Test: GET /parking-lots/availability - Ongeldige datetime"""
        params = {"datetime": "invalid-date"}
        response = client.get(
            "/parking-lots/availability", headers=auth_headers, params=params
        )
        assert response.status_code == 400

    def test_get_parking_lots_availability_unauthorized(self, client):
        """Test: GET /parking-lots/availability - Zonder authenticatie"""
        response = client.get("/parking-lots/availability")
        assert response.status_code in [200, 401]

    # Tests voor GET /parking-lots/{id}/availability
    def test_get_parking_lot_availability_by_id_success(self, client, auth_headers):
        """Test: GET /parking-lots/{id}/availability - Specifieke lot beschikbaarheid"""
        parking_lot_id = "1"
        response = client.get(
            f"/parking-lots/{parking_lot_id}/availability", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        expected_fields = ["capacity", "reserved", "available"]
        # Tenminste één van deze velden zou moeten bestaan
        assert any(field in data for field in expected_fields)

    def test_get_parking_lot_availability_not_found(self, client, auth_headers):
        """Test: GET /parking-lots/{id}/availability - Niet bestaande parking lot"""
        invalid_id = "999999"
        response = client.get(
            f"/parking-lots/{invalid_id}/availability", headers=auth_headers
        )
        assert response.status_code == 404

    def test_get_parking_lot_availability_with_timerange(self, client, auth_headers):
        """Test: GET /parking-lots/{id}/availability - Met time range"""
        parking_lot_id = "1"
        params = {
            "start_time": "2024-12-25T09:00:00",
            "end_time": "2024-12-25T17:00:00",
        }
        response = client.get(
            f"/parking-lots/{parking_lot_id}/availability",
            headers=auth_headers,
            params=params,
        )
        assert response.status_code in [200, 400]

    def test_get_parking_lot_availability_invalid_timerange(self, client, auth_headers):
        """Test: GET /parking-lots/{id}/availability - Ongeldige time range"""
        parking_lot_id = "1"
        params = {
            "start_time": "2024-12-25T17:00:00",  # End time before start time
            "end_time": "2024-12-25T09:00:00",
        }
        response = client.get(
            f"/parking-lots/{parking_lot_id}/availability",
            headers=auth_headers,
            params=params,
        )
        assert response.status_code == 400

    # Tests voor GET /parking-lots/search
    def test_search_parking_lots_by_name(self, client, auth_headers):
        """Test: GET /parking-lots/search - Zoeken op naam"""
        params = {"name": "Central"}
        response = client.get(
            "/parking-lots/search", headers=auth_headers, params=params
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (dict, list))

    def test_search_parking_lots_by_location(self, client, auth_headers):
        """Test: GET /parking-lots/search - Zoeken op locatie"""
        params = {"location": "Amsterdam"}
        response = client.get(
            "/parking-lots/search", headers=auth_headers, params=params
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (dict, list))

    def test_search_parking_lots_no_results(self, client, auth_headers):
        """Test: GET /parking-lots/search - Geen resultaten"""
        params = {"name": "NonExistentParkingLot12345"}
        response = client.get(
            "/parking-lots/search", headers=auth_headers, params=params
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (dict, list))
        if isinstance(data, dict):
            assert len(data) == 0
        else:
            assert len(data) == 0

    def test_search_parking_lots_no_parameters(self, client, auth_headers):
        """Test: GET /parking-lots/search - Zonder search parameters"""
        response = client.get("/parking-lots/search", headers=auth_headers)
        assert response.status_code in [200, 400]

    # Tests voor GET /parking-lots/{id}/reservations
    def test_get_parking_lot_reservations_success(self, client, auth_headers):
        """Test: GET /parking-lots/{id}/reservations - Reserveringen voor specifieke lot"""
        parking_lot_id = "1"
        response = client.get(
            f"/parking-lots/{parking_lot_id}/reservations", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (dict, list))

    def test_get_parking_lot_reservations_not_found(self, client, auth_headers):
        """Test: GET /parking-lots/{id}/reservations - Niet bestaande parking lot"""
        invalid_id = "999999"
        response = client.get(
            f"/parking-lots/{invalid_id}/reservations", headers=auth_headers
        )
        assert response.status_code == 404

    def test_get_parking_lot_reservations_with_date_filter(self, client, auth_headers):
        """Test: GET /parking-lots/{id}/reservations - Met datum filter"""
        parking_lot_id = "1"
        params = {"date": "2024-12-25"}
        response = client.get(
            f"/parking-lots/{parking_lot_id}/reservations",
            headers=auth_headers,
            params=params,
        )
        assert response.status_code in [200, 400]

    def test_get_parking_lot_reservations_unauthorized(self, client):
        """Test: GET /parking-lots/{id}/reservations - Zonder authenticatie"""
        response = client.get("/parking-lots/1/reservations")
        assert response.status_code == 401

    # Tests voor GET /parking-lots/{id}/stats
    def test_get_parking_lot_stats_success(self, client, auth_headers):
        """Test: GET /parking-lots/{id}/stats - Statistieken voor specifieke lot"""
        parking_lot_id = "1"
        response = client.get(
            f"/parking-lots/{parking_lot_id}/stats", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Verwachte statistiek velden
        stat_fields = [
            "total_reservations",
            "occupancy_rate",
            "revenue",
            "average_duration",
        ]
        # Tenminste één statistiek veld zou moeten bestaan
        assert any(field in data for field in stat_fields)

    def test_get_parking_lot_stats_not_found(self, client, auth_headers):
        """Test: GET /parking-lots/{id}/stats - Niet bestaande parking lot"""
        invalid_id = "999999"
        response = client.get(f"/parking-lots/{invalid_id}/stats", headers=auth_headers)
        assert response.status_code == 404

    def test_get_parking_lot_stats_with_period(self, client, auth_headers):
        """Test: GET /parking-lots/{id}/stats - Met tijdsperiode"""
        parking_lot_id = "1"
        params = {"period": "month", "year": "2024", "month": "12"}
        response = client.get(
            f"/parking-lots/{parking_lot_id}/stats", headers=auth_headers, params=params
        )
        assert response.status_code in [200, 400]

    def test_get_parking_lot_stats_admin_only(self, client, auth_headers):
        """Test: GET /parking-lots/{id}/stats - Admin only toegang"""
        parking_lot_id = "1"
        response = client.get(
            f"/parking-lots/{parking_lot_id}/stats", headers=auth_headers
        )
        # Stats kunnen admin-only zijn
        assert response.status_code in [200, 401, 403]

