from api.tests.conftest import get_last_pid

# Tests voor GET /parking-lots
def test_get_all_parking_lots_success(client_with_token):
    """Test: GET /parking-lots - Succesvol ophalen alle parking lots"""
    user_client, headers = client_with_token("user")
    response = user_client.get("/parking-lots/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data[0]["name"] == "Bedrijventerrein Almere Parkeergarage"
    assert data[1]["name"] == "Vlaardingen Evenementenhal Parkeerterrein"
    assert len(data) == 2

def test_get_all_parking_lots_unauthorized(client):
    """Test: GET /parking-lots - Zonder authenticatie"""
    response = client.get("/parking-lots/")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["name"] == "Bedrijventerrein Almere Parkeergarage"
    assert data[1]["name"] == "Vlaardingen Evenementenhal Parkeerterrein"
    assert len(data) == 2

def test_get_all_parking_lots_empty(client_with_token):
    """Test: GET /parking-lots - Lege parking lots lijst"""
    # Superadmin gets all the parking lots, and deletes tem all.
    superadmin_client, headers = client_with_token("superadmin")
    response = superadmin_client.get("/parking-lots/", headers=headers)
    data = response.json()
    assert len(data) == 2
    for parking_lot in data:
        superadmin_client.delete(f"/parking-lots/{parking_lot['id']}", headers=headers)

    response = superadmin_client.get("/parking-lots/", headers=headers)
    assert response.status_code == 204

# Tests voor GET /parking-lots/{id}

def test_get_parking_lot_by_lid_success(client):
    """Test: GET /parking-lots/{id} - Succesvol ophalen parking lot"""

    parking_lot_id = get_last_pid(client)

    # TEst if we can get a specific parking lot
    response = client.get(f"/parking-lots/{parking_lot_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data["name"] == "Vlaardingen Evenementenhal Parkeerterrein"
    assert data["location"] == "Event Center"
    assert data["capacity"] == 50

def test_get_parking_lot_by_lid_not_found(client):
    """Test: GET /parking-lots/{id} - Niet bestaande parking lot"""
    response = client.get(f"/parking-lots/9999")
    assert response.status_code == 404

def test_get_parking_lot_by_lid_unauthorized(client):
    """Test: GET /parking-lots/{id} - Zonder authenticatie"""
    parking_lot_id = get_last_pid(client)
    response = client.get(f"/parking-lots/{parking_lot_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == parking_lot_id

# Tests voor GET /parking-lots/location/{location}
def test_get_parking_lots_by_location_success(client):
    """Test: GET /parking-lots/location/{location} - Parking lots op specifieke locatie"""
    location = "Industrial Zone"
    response = client.get(f"/parking-lots/location/{location}")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["location"] == "Industrial Zone"

def test_get_parking_lots_by_location_not_found(client):
    """Test: GET /parking-lots/location/{location} - Geen parking lots op locatie"""
    location = "NonExistentLocation"
    response = client.get(f"/parking-lots/location/{location}")
    assert response.status_code == 404
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 1
    assert "detail" in data

def test_get_parking_lots_by_location_unauthorized(client):
    """Test: GET /parking-lots/location/{location} - Zonder authenticatie"""
    location = "Industrial Zone"
    response = client.get(f"/parking-lots/location/{location}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["location"] == "Industrial Zone"

def test_get_parking_lots_sessions(client_with_token):
    """Test: GET /parking-lots/{id}/sessions - Alle sessies van een parking lot"""
    superadmin_client, headers = client_with_token("superadmin")
    parking_lot_id = get_last_pid(superadmin_client)
    response = superadmin_client.get(f"/parking-lots/{parking_lot_id}/sessions", headers=headers, params={"lid": parking_lot_id})
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 0

def test_get_parking_lots_sessions_by_id_no_session(client_with_token):
    """Test: GET /parking-lots/{id}/sessions - Alle sessies van een parking lot"""
    superadmin_client, headers = client_with_token("superadmin")
    parking_lot_id = get_last_pid(superadmin_client)
    response = superadmin_client.get(f"/parking-lots/{parking_lot_id}/sessions/99999", headers=headers, params={"lid": parking_lot_id, "sid": 999999})
    assert response.status_code == 404

    data = response.json()
    assert data["detail"]["error"] == "Session not found"


# Tests voor GET /parking-lots/availability
#def test_get_parking_lots_availability_success():
#    """Test: GET /parking-lots/availability - Beschikbaarheid alle lots"""
#    response = client.get("/parking-lots/availability")
#    assert response.status_code == 200
#    data = response.json()
#    assert isinstance(data, dict)
#    assert "1" in data
#    assert "capacity" in data["1"]
#    assert "available" in data["1"]

#def test_get_parking_lots_availability_unauthorized():
#    """Test: GET /parking-lots/availability - Zonder authenticatie"""
#    response = client.get("/parking-lots/availability")
#    assert response.status_code == 401

# Tests voor GET /parking-lots/{id}/availability
#def test_get_parking_lot_availability_by_id_success():
#    """Test: GET /parking-lots/{id}/availability - Specifieke lot beschikbaarheid"""
#    parking_lot_id = "1"
#    response = client.get(f"/parking-lots/{parking_lot_id}/availability")
#    assert response.status_code == 200
#    data = response.json()
#    assert isinstance(data, dict)
#    assert "capacity" in data
#    assert "available" in data

#def test_get_parking_lot_availability_not_found():
#    """Test: GET /parking-lots/{id}/availability - Niet bestaande parking lot"""
#    invalid_id = "999999"
#    response = client.get(f"/parking-lots/{invalid_id}/availability")
#    assert response.status_code == 404

# Tests voor GET /parking-lots/search
#def test_search_parking_lots_by_name():
#    """Test: GET /parking-lots/search - Zoeken op naam"""
#    params = {"name": "Almere"}
#    response = client.get("/parking-lots/search", params=params)
#    assert response.status_code == 200
#    data = response.json()
#    assert isinstance(data, dict)

#def test_search_parking_lots_unauthorized():
#    """Test: GET /parking-lots/search - Zonder authenticatie"""
#    response = client.get("/parking-lots/search")
#    assert response.status_code == 401

# Tests voor GET /parking-lots/city/{city}
#def test_get_parking_lots_by_city_success():
#    """Test: GET /parking-lots/city/{city} - Parking lots in specifieke stad"""
#    city = "Almere"
#    response = client.get(f"/parking-lots/city/{city}")
#    assert response.status_code == 200
#    data = response.json()
#    assert isinstance(data, dict)
#    assert "1" in data
#    assert data["1"]["name"] == "Bedrijventerrein Almere Parkeergarage"

#def test_get_parking_lots_by_city_not_found():
#    """Test: GET /parking-lots/city/{city} - Geen parking lots in stad"""
#    city = "NonExistentCity"
#    response = client.get(f"/parking-lots/city/{city}")
#    assert response.status_code == 200
#    data = response.json()
#    assert isinstance(data, dict)
#    assert len(data) == 0

#def test_get_parking_lots_by_city_unauthorized():
#    """Test: GET /parking-lots/city/{city} - Zonder authenticatie"""
#    city = "Almere"
#    response = client.get(f"/parking-lots/city/{city}")
#    assert response.status_code == 401

# Tests voor GET /parking-lots/{id}/reservations
#def test_get_parking_lot_reservations_success(client_with_token):
#    """Test: GET /parking-lots/{id}/reservations - Reserveringen voor specifieke lot"""
#    client, headers = client_with_token("superadmin")
#    parking_lot_id = "1"
#    response = client.get(f"/parking-lots/{parking_lot_id}/reservations", headers=headers)
#    assert response.status_code == 200
#    data = response.json()
#    assert isinstance(data, list)

#def test_get_parking_lot_reservations_unauthorized():
#    """Test: GET /parking-lots/{id}/reservations - Zonder authenticatie"""
#    response = client.get("/parking-lots/1/reservations")
#    assert response.status_code == 401

# Tests voor GET /parking-lots/{id}/stats
#def test_get_parking_lot_stats_success(mock_db, valid_admin_headers):
#    """Test: GET /parking-lots/{id}/stats - Statistieken voor specifieke lot"""
#    parking_lot_id = "1"
#    response = client.get(f"/parking-lots/{parking_lot_id}/stats", headers=valid_admin_headers)
#    assert response.status_code == 200
#    data = response.json()
#    assert isinstance(data, dict)
#    assert "total_reservations" in data
#    assert "occupancy_rate" in data

#def test_get_parking_lot_stats_unauthorized():
#    """Test: GET /parking-lots/{id}/stats - Zonder authenticatie"""
#    response = client.get("/parking-lots/1/stats")
#    assert response.status_code == 401
#def test_get_parking_lot_stats_forbidden(client_with_token):
#    """Test: GET /parking-lots/{id}/stats - Normale user toegang geweigerd"""
#    client, headers = client_with_token("user")
#    response = client.get(f"/parking-lots/1/stats", headers=headers)
#    assert response.status_code == 403