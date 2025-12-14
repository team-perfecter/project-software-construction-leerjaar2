import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.auth_utils import create_access_token
from api.models.user_model import UserModel
from api.models.payment_model import PaymentModel
from api.datatypes.payment import PaymentCreate


pytest_plugins = "pytest_benchmark"

def pytest_configure(config):
    config.option.benchmark_min_rounds = 20


@pytest.fixture(scope="session")
def base_client():
    """Provides a FastAPI TestClient instance (session-scoped for reuse)."""
    return TestClient(app)

@pytest.fixture
def client(base_client):
    """Provides access to the session-scoped client."""
    return base_client


@pytest.fixture
def client_with_token(base_client):
    """
    Returns a TestClient and headers with JWT token for a given role.
    Uses session-scoped client for better performance.
    """

    def _client_with_role(username: str):
        token = create_access_token({"sub": username})
        headers = {"Authorization": f"Bearer {token}"}
        return base_client, headers

    return _client_with_role

@pytest.fixture(autouse=True)
def setup_vehicles(request, client_with_token):
    """
    Clears the database of vehicles before each test.
    If the test is not testing vehicle creation, it also adds a default vehicle.
    This fixture handles different response structures from /vehicles endpoint.
    """
    client, headers = client_with_token("superadmin")

    # Haal alle voertuigen op
    response = client.get("/vehicles", headers=headers)
    try:
        data = response.json()
    except Exception:
        data = []

    # Zorg dat we altijd een lijst van voertuigen hebben
    if isinstance(data, dict):
        # Bijvoorbeeld: {"message": "Vehicles not found"} → geen voertuigen
        vehicles_list = []
    elif isinstance(data, list):
        vehicles_list = data
    else:
        # Onverwachte response
        vehicles_list = []

    # Verwijder alle bestaande voertuigen
    for vehicle in vehicles_list:
        # Controleer of vehicle dict is en 'id' bevat
        if isinstance(vehicle, dict) and "id" in vehicle:
            client.delete(f"/vehicles/delete/{vehicle['id']}", headers=headers)

    # Voeg een standaard voertuig toe als de test geen create test is
    if "create" not in request.node.fspath.basename:
        vehicle = {
            "user_id": 1,
            "license_plate": "ABC123",
            "make": "Toyota",
            "model": "Corolla",
            "color": "Blue",
            "year": 2020,
        }
        client.post("/vehicles/create", json=vehicle, headers=headers)


@pytest.fixture(autouse=True)
def setup_users(request, client_with_token):
    """
    Clears the database of users.
    If the create endpoints are not being tested, this also adds 2 users to the database
    """

    client, headers = client_with_token("superadmin")
    response = client.get("/users/", headers=headers)
    

    if "create" not in request.node.fspath.basename:
        for user in response.json():
            if user['id'] != 1:
                client.delete(f"/users/{user['id']}", headers=headers)

        user2 = {
            "username": "admin",
            "password": "admin123",
            "email": "bla@bla.com",
            "name": "admin",
            "role": "admin"
        }    
    
        user3 = {
            "username": "paymentadmin",
            "password": "admin123",
            "email": "bla@bla.com",
            "name": "paymentadmin",
            "role": "paymentadmin"
        }

        user4 = {
            "username": "user",
            "password": "admin123",
            "email": "bla@bla.com",
            "name": "user",
            "role": "user"
        }

        user5 = {
            "username": "extrauser",
            "password": "admin123",
            "email": "bla@bla.com",
            "name": "extrauser",
            "role": "user"
        }

        client.post("/create_user", json=user2, headers=headers)
        client.post("/create_user", json=user3, headers=headers)
        client.post("/create_user", json=user4, headers=headers)
        client.post("/create_user", json=user5, headers=headers)

@pytest.fixture(autouse=True, scope="function")
def setup_parking_lots(request, client_with_token):
    """
    Fixture to ensure parking lots exist before tests and clean up after.
    Optimized for speed.
    """

    client, headers = client_with_token("superadmin")

    # Skip cleanup for read-only tests (GET endpoints)
    is_readonly_test = any(keyword in request.node.name.lower() for keyword in ["get", "read", "list"])
    
    if not is_readonly_test:
        # Only cleanup if test modifies data
        _cleanup_all(client, headers)

    # Create default parking lots if not testing create endpoints
    if "create" not in request.node.fspath.basename:
        _ensure_parking_lots_exist(client, headers)


def _cleanup_all(client, headers):
    """Fast cleanup using batch operations where possible."""
    try:
        # Get all parking lots once
        lots_response = client.get("/parking-lots/", headers=headers)
        if lots_response.status_code != 200:
            return
        
        lots = lots_response.json()
        
        # Delete sessions for all parking lots
        for lot in lots:
            lot_id = lot['id']
            try:
                # Get sessions
                sessions_response = client.get(f"/parking-lots/{lot_id}/sessions", headers=headers)
                if sessions_response.status_code == 200:
                    sessions = sessions_response.json()
                    # Delete sessions without individual error handling
                    for session in sessions:
                        client.delete(
                            f"/parking-lots/{lot_id}/sessions/{session['id']}", 
                            headers=headers
                        )
            except:
                pass  # Silently continue
        
        # Delete all reservations in one go
        try:
            reservations_response = client.get("/reservations/all", headers=headers)
            if reservations_response.status_code == 200:
                for reservation in reservations_response.json():
                    client.delete(
                        f"/reservations/delete/{reservation['id']}", 
                        headers=headers
                    )
        except:
            pass
        
        # Delete parking lots
        for lot in lots:
            try:
                client.delete(f"/parking-lots/{lot['id']}", headers=headers)
            except:
                pass
    except:
        pass  # Fail silently


def _ensure_parking_lots_exist(client, headers):
    """Only create parking lots if they don't exist."""
    try:
        response = client.get("/parking-lots/", headers=headers)
        if response.status_code == 200 and len(response.json()) >= 2:
            return  # Parking lots already exist
    except:
        pass
    
    # Create parking lots
    lot_data = [
        {
            "name": "Bedrijventerrein Almere Parkeergarage",
            "location": "Industrial Zone",
            "address": "Schanssingel 337, 2421 BS Almere",
            "capacity": 100,
            "tariff": 0.5,
            "daytariff": 0.5,
            "lat": 0,
            "lng": 0,
        },
        {
            "name": "Vlaardingen Evenementenhal Parkeerterrein",
            "location": "Event Center",
            "address": "Westlindepark 756, 8920 AB Vlaardingen",
            "capacity": 50,
            "tariff": 0.5,
            "daytariff": 0.5,
            "lat": 0,
            "lng": 0,
        }
    ]
    
    for lot in lot_data:
        try:
            client.post("/parking-lots", json=lot, headers=headers)
        except:
            pass


# region HELPER FUNCTIONS FOR TESTS


# Cache voor parking lot IDs
_parking_lot_cache = {}



def get_last_pid(client):
    """
    Gets the ID of the last parking lot in the database.
    Uses caching for better performance.
    """
    cache_key = "last_pid"
    
    # Return cached value if available
    if cache_key in _parking_lot_cache:
        return _parking_lot_cache[cache_key]
    
    response = client.get("/parking-lots/")

    if response.status_code != 200:
        pytest.fail(f"Failed to get parking lots: {response.status_code}")

    data = response.json()

    if not data or len(data) == 0:
        pytest.fail("No parking lots found in database")

    pid = data[-1]["id"]
    _parking_lot_cache[cache_key] = pid
    return pid


def create_test_vehicle(client, headers, license_plate="TEST-VEHICLE"):
    """
    Creates a test vehicle for the authenticated user.
    Optimized version with reduced API calls.
    """
    # Get authenticated user's ID (cache this if possible)
    profile_response = client.get("/profile", headers=headers)
    if profile_response.status_code != 200:
        pytest.fail(f"Failed to get user profile: {profile_response.status_code}")

    user_id = profile_response.json()["id"]

    # Create vehicle
    vehicle_data = {
        "user_id": user_id,
        "license_plate": license_plate,
        "make": "Toyota",
        "model": "Corolla",
        "color": "Blue",
        "year": 2024,
    }

    create_response = client.post(
        "/vehicles/create", json=vehicle_data, headers=headers
    )

    if create_response.status_code != 201:
        pytest.fail(f"Failed to create vehicle: {create_response.status_code}")

    # Try to extract ID from creation response first
    try:
        created_data = create_response.json()
        if isinstance(created_data, dict) and "id" in created_data:
            return created_data["id"]
    except:
        pass

    # Fallback: Get vehicle ID from GET /vehicles
    vehicles_response = client.get("/vehicles", headers=headers)

    if vehicles_response.status_code != 200:
        pytest.fail(f"Failed to get vehicles: {vehicles_response.status_code}")

    vehicles = vehicles_response.json()

    if not vehicles or len(vehicles) == 0:
        pytest.fail("No vehicles found after creation")

    last_vehicle = vehicles[-1]

    # Handle both tuple and dict responses
    if isinstance(last_vehicle, (tuple, list)):
        return last_vehicle[0]
    elif isinstance(last_vehicle, dict):
        return last_vehicle["id"]
    else:
        pytest.fail(f"Unexpected vehicle response format: {type(last_vehicle)}")


def create_test_parking_lot(client, headers, name="Test Parking Lot"):
    """
    Creates a test parking lot (requires superadmin).
    Optimized version.
    """
    parking_lot_data = {
        "name": name,
        "location": "Test Location",
        "address": "Test Address 123",
        "capacity": 100,
        "tariff": 2.5,
        "daytariff": 20.0,
        "lat": 52.0,
        "lng": 4.0,
    }

    create_response = client.post(
        "/parking-lots", json=parking_lot_data, headers=headers
    )

    if create_response.status_code != 201:
        pytest.fail(f"Failed to create parking lot: {create_response.status_code}")

    # Try to get ID from response
    try:
        data = create_response.json()
        if isinstance(data, dict) and "id" in data:
            return data["id"]
    except:
        pass

    # Fallback: Get the last parking lot ID
    response = client.get("/parking-lots/")
    if response.status_code == 200:
        parking_lots = response.json()
        if parking_lots and len(parking_lots) > 0:
            return parking_lots[-1]["id"]

    pytest.fail("Could not retrieve parking lot ID after creation")


def setup_reservation_prerequisites(
    client_with_token, role="user", vehicle_plate="TEST-RES", lot_name="Test Lot"
):
    """
    Sets up both a vehicle and parking lot for reservation/session tests.
    Reuses existing parking lots when possible.
    """
    # Get client with user role
    user_client, user_headers = client_with_token(role)

    # Create vehicle as user
    vehicle_id = create_test_vehicle(user_client, user_headers, vehicle_plate)

    # Always use existing parking lot (created by fixture)
    response = user_client.get("/parking-lots/")
    if response.status_code == 200 and response.json():
        parking_lot_id = response.json()[-1]["id"]
    else:
        # Fallback: create if needed
        superadmin_client, superadmin_headers = client_with_token("superadmin")
        parking_lot_id = create_test_parking_lot(
            superadmin_client, superadmin_headers, lot_name
        )

    return user_client, user_headers, vehicle_id, parking_lot_id


def setup_session_prerequisites(
    client_with_token, role="user", vehicle_plate="TEST-SESSION"
):
    """
    Sets up vehicle and parking lot for session tests.
    Alias for setup_reservation_prerequisites for clarity in session tests.
    """
    return setup_reservation_prerequisites(
        client_with_token, role, vehicle_plate, "Session Test Lot"
    )


# endregion
    return data[-1]["id"]


@pytest.fixture(autouse=True)
def setup_payments(request, client_with_token):
    """
    Clears all payments for superadmin.
    If the create endpoints are not being tested, adds 5 payments to the DB.
    """
    user_model = UserModel()

    client, headers = client_with_token("superadmin")

    # Get superadmin
    user = user_model.get_user_by_username("superadmin")
    if not user:
        raise Exception("Superadmin must exist in the DB for benchmarks")

    # Delete all existing payments for superadmin
    response = client.get("/payments/me", headers=headers)
    if response.status_code == 200:
        for payment in response.json():
            client.delete(f"/payments/{payment['id']}", headers=headers)

    # Seed 5 payments if not testing creation endpoints
    if "create" not in request.node.fspath.basename:
        for i in range(5):
            payment = {
                "user_id": user.id,
                "transaction": f"transaction{i+1}",
                "amount": 100 + i,
                "hash": f"hash{i+1}",
                "method": f"method{i+1}",
                "issuer": f"issuer{i+1}",
                "bank": f"bank{i+1}"
            }
            client.post("/payments", json=payment, headers=headers)
            

def get_last_payment_id(client_with_token):
    """
    Returns the ID of the last payment for superadmin.
    Useful to make sure the payment you test exists.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/me", headers=headers)
    data = response.json()
    return data[-1]["id"]


def get_last_uid(client_with_token):
    """
    Returns the id of the last user.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/users/", headers=headers)
    data = response.json()
    return data[-1]["id"]

def get_last_vid(client_with_token):
    """
    Returns the ID of the last vehicle in the database.
    Creates a vehicle if none exists.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/vehicles", headers=headers)
    data = response.json()
    return data[-1]["id"]
