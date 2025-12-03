from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

# Secret key en algorithm voor token creation
SECRET_KEY = "test-secret-key"
ALGORITHM = "HS256"

def create_test_token(username: str, role: str = "USER"):
    expire = datetime.utcnow() + timedelta(minutes=30)
    token = jwt.encode({"sub": username, "exp": expire, "role": role}, SECRET_KEY, algorithm=ALGORITHM)
    return token

@pytest.fixture
def valid_user_token():
    return create_test_token("testuser")

@pytest.fixture
def valid_admin_token():
    return create_test_token("admin", role="ADMIN")

@pytest.fixture
def valid_user_headers(valid_user_token):
    return {"Authorization": f"Bearer {valid_user_token}"}

@pytest.fixture
def valid_admin_headers(valid_admin_token):
    return {"Authorization": f"Bearer {valid_admin_token}"}

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

def get_fake_parking_lot(lid: str):
    parking_lots = get_fake_parking_lots()
    return parking_lots.get(lid)

def get_fake_availability_data():
    return {
        "1": {"capacity": 335, "reserved": 77, "available": 258},
        "2": {"capacity": 730, "reserved": 136, "available": 594}
    }

def get_fake_search_results(query_params):
    all_lots = get_fake_parking_lots()
    if "name" in query_params:
        return {k: v for k, v in all_lots.items() if query_params["name"].lower() in v["name"].lower()}
    if "location" in query_params:
        return {k: v for k, v in all_lots.items() if query_params["location"].lower() in v["location"].lower()}
    return {}

def get_fake_city_results(city: str):
    all_lots = get_fake_parking_lots()
    if city.lower() == "almere":
        return {"1": all_lots["1"]}
    elif city.lower() == "vlaardingen":
        return {"2": all_lots["2"]}
    return {}

def get_fake_location_results(location: str):
    all_lots = get_fake_parking_lots()
    if location.lower() == "industrial zone":
        return {"1": all_lots["1"]}
    elif location.lower() == "event center":
        return {"2": all_lots["2"]}
    return {}

def get_fake_reservations(lid: str):
    return [
        {
            "id": "1",
            "parking_lot_id": lid,
            "user_id": "1",
            "vehicle_id": "123",
            "start_time": "2024-12-25T09:00:00Z",
            "end_time": "2024-12-25T17:00:00Z",
            "status": "confirmed"
        }
    ]

def get_fake_stats(lid: str):
    return {
        "total_reservations": 150,
        "occupancy_rate": 0.75,
        "revenue": 1250.50,
        "average_duration": 4.5
    }

# Tests voor GET /parking-lots
@patch("db_get_all_parking_lots", return_value=get_fake_parking_lots())
def test_get_all_parking_lots_success(mock_db, valid_user_headers):
    """Test: GET /parking-lots - Succesvol ophalen alle parking lots"""
    response = client.get("/parking-lots", headers=valid_user_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "1" in data
    assert "name" in data["1"]
    assert "location" in data["1"]

def test_get_all_parking_lots_unauthorized():
    """Test: GET /parking-lots - Zonder authenticatie"""
    response = client.get("/parking-lots")
    assert response.status_code == 401

@patch("db_get_all_parking_lots", return_value={})
def test_get_all_parking_lots_empty(mock_db, valid_user_headers):
    """Test: GET /parking-lots - Lege parking lots lijst"""
    response = client.get("/parking-lots", headers=valid_user_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 0

# Tests voor GET /parking-lots/{id}
@patch("db_get_parking_lot", side_effect=get_fake_parking_lot)
def test_get_parking_lot_by_lid_success(mock_db, valid_user_headers):
    """Test: GET /parking-lots/{id} - Succesvol ophalen parking lot"""
    parking_lot_id = "1"
    response = client.get(f"/parking-lots/{parking_lot_id}", headers=valid_user_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data["name"] == "Bedrijventerrein Almere Parkeergarage"
    assert data["location"] == "Industrial Zone"
    assert data["capacity"] == 335

@patch("db_get_parking_lot", return_value=None)
def test_get_parking_lot_by_lid_not_found(mock_db, valid_user_headers):
    """Test: GET /parking-lots/{id} - Niet bestaande parking lot"""
    invalid_id = "999999"
    response = client.get(f"/parking-lots/{invalid_id}", headers=valid_user_headers)
    assert response.status_code == 404

def test_get_parking_lot_by_lid_unauthorized():
    """Test: GET /parking-lots/{id} - Zonder authenticatie"""
    response = client.get("/parking-lots/1")
    assert response.status_code == 401

# Tests voor GET /parking-lots/availability
@patch("db_get_availability_all", return_value=get_fake_availability_data())
def test_get_parking_lots_availability_success(mock_db, valid_user_headers):
    """Test: GET /parking-lots/availability - Beschikbaarheid alle lots"""
    response = client.get("/parking-lots/availability", headers=valid_user_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "1" in data
    assert "capacity" in data["1"]
    assert "available" in data["1"]

def test_get_parking_lots_availability_unauthorized():
    """Test: GET /parking-lots/availability - Zonder authenticatie"""
    response = client.get("/parking-lots/availability")
    assert response.status_code == 401

# Tests voor GET /parking-lots/{id}/availability
@patch("db_get_availability", return_value={"capacity": 335, "reserved": 77, "available": 258})
def test_get_parking_lot_availability_by_id_success(mock_db, valid_user_headers):
    """Test: GET /parking-lots/{id}/availability - Specifieke lot beschikbaarheid"""
    parking_lot_id = "1"
    response = client.get(f"/parking-lots/{parking_lot_id}/availability", headers=valid_user_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "capacity" in data
    assert "available" in data

@patch("db_get_availability", return_value=None)
def test_get_parking_lot_availability_not_found(mock_db, valid_user_headers):
    """Test: GET /parking-lots/{id}/availability - Niet bestaande parking lot"""
    invalid_id = "999999"
    response = client.get(f"/parking-lots/{invalid_id}/availability", headers=valid_user_headers)
    assert response.status_code == 404

# Tests voor GET /parking-lots/search
@patch("db_search_parking_lots", side_effect=get_fake_search_results)
def test_search_parking_lots_by_name(mock_db, valid_user_headers):
    """Test: GET /parking-lots/search - Zoeken op naam"""
    params = {"name": "Almere"}
    response = client.get("/parking-lots/search", headers=valid_user_headers, params=params)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)

def test_search_parking_lots_unauthorized():
    """Test: GET /parking-lots/search - Zonder authenticatie"""
    response = client.get("/parking-lots/search")
    assert response.status_code == 401

# Tests voor GET /parking-lots/city/{city}
@patch("db_get_parking_lots_by_city", side_effect=get_fake_city_results)
def test_get_parking_lots_by_city_success(mock_db, valid_user_headers):
    """Test: GET /parking-lots/city/{city} - Parking lots in specifieke stad"""
    city = "Almere"
    response = client.get(f"/parking-lots/city/{city}", headers=valid_user_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "1" in data
    assert data["1"]["name"] == "Bedrijventerrein Almere Parkeergarage"

@patch("db_get_parking_lots_by_city", return_value={})
def test_get_parking_lots_by_city_not_found(mock_db, valid_user_headers):
    """Test: GET /parking-lots/city/{city} - Geen parking lots in stad"""
    city = "NonExistentCity"
    response = client.get(f"/parking-lots/city/{city}", headers=valid_user_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 0

def test_get_parking_lots_by_city_unauthorized():
    """Test: GET /parking-lots/city/{city} - Zonder authenticatie"""
    city = "Almere"
    response = client.get(f"/parking-lots/city/{city}")
    assert response.status_code == 401

# Tests voor GET /parking-lots/location/{location}
@patch("db_get_parking_lots_by_location", side_effect=get_fake_location_results)
def test_get_parking_lots_by_location_success(mock_db, valid_user_headers):
    """Test: GET /parking-lots/location/{location} - Parking lots op specifieke locatie"""
    location = "Industrial Zone"
    response = client.get(f"/parking-lots/location/{location}", headers=valid_user_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "1" in data
    assert data["1"]["location"] == "Industrial Zone"

@patch("db_get_parking_lots_by_location", return_value={})
def test_get_parking_lots_by_location_not_found(mock_db, valid_user_headers):
    """Test: GET /parking-lots/location/{location} - Geen parking lots op locatie"""
    location = "NonExistentLocation"
    response = client.get(f"/parking-lots/location/{location}", headers=valid_user_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 0

def test_get_parking_lots_by_location_unauthorized():
    """Test: GET /parking-lots/location/{location} - Zonder authenticatie"""
    location = "Industrial Zone"
    response = client.get(f"/parking-lots/location/{location}")
    assert response.status_code == 401

# Tests voor GET /parking-lots/{id}/reservations
@patch("db_get_parking_lot_reservations", side_effect=get_fake_reservations)
def test_get_parking_lot_reservations_success(mock_db, valid_user_headers):
    """Test: GET /parking-lots/{id}/reservations - Reserveringen voor specifieke lot"""
    parking_lot_id = "1"
    response = client.get(f"/parking-lots/{parking_lot_id}/reservations", headers=valid_user_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_parking_lot_reservations_unauthorized():
    """Test: GET /parking-lots/{id}/reservations - Zonder authenticatie"""
    response = client.get("/parking-lots/1/reservations")
    assert response.status_code == 401

# Tests voor GET /parking-lots/{id}/stats
@patch("db_get_parking_lot_stats", side_effect=get_fake_stats)
def test_get_parking_lot_stats_success(mock_db, valid_admin_headers):
    """Test: GET /parking-lots/{id}/stats - Statistieken voor specifieke lot"""
    parking_lot_id = "1"
    response = client.get(f"/parking-lots/{parking_lot_id}/stats", headers=valid_admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "total_reservations" in data
    assert "occupancy_rate" in data

def test_get_parking_lot_stats_unauthorized():
    """Test: GET /parking-lots/{id}/stats - Zonder authenticatie"""
    response = client.get("/parking-lots/1/stats")
    assert response.status_code == 401

@patch("get_current_user", return_value={"username": "testuser", "role": "USER"})
def test_get_parking_lot_stats_forbidden(mock_user, valid_user_headers):
    """Test: GET /parking-lots/{id}/stats - Normale user toegang geweigerd"""
    parking_lot_id = "1"
    response = client.get(f"/parking-lots/{parking_lot_id}/stats", headers=valid_user_headers)
    assert response.status_code == 403