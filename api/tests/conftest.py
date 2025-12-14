import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.auth_utils import create_access_token


@pytest.fixture
def client():
    """Provides a FastAPI TestClient instance."""
    return TestClient(app)


@pytest.fixture
def client_with_token(client):
    """
    Returns a TestClient and headers with JWT token for a given role.

    Usage:
        client, headers = client_with_token("superadmin")
        client, headers = client_with_token("paymentadmin")
    """

    def _client_with_role(username: str):
        token = create_access_token({"sub": username})
        headers = {"Authorization": f"Bearer {token}"}
        return client, headers

    return _client_with_role


@pytest.fixture(autouse=True)
def setup_parking_lots(request, client_with_token):
    """
    Clears the database of parking lots.
    If the create endpoints are not being tested, this also adds 2 parking lots to the database
    """
    # Get superadmin client
    client, headers = client_with_token("superadmin")

    # ✅ FIRST: Delete all reservations to avoid foreign key constraint violations
    try:
        # Get all users to delete their reservations
        users_response = client.get("/admin/users", headers=headers)
        if users_response.status_code == 200:
            users = users_response.json()
            for user in users:
                # Delete reservations for each user
                reservations_response = client.get(
                    f"/reservations/user/{user['id']}", headers=headers
                )
                if reservations_response.status_code == 200:
                    reservations = reservations_response.json()
                    for reservation in reservations:
                        client.delete(
                            f"/reservations/delete/{reservation['id']}", headers=headers
                        )
    except Exception as e:
        print(f"Warning: Could not delete reservations: {e}")

    # ✅ SECOND: Delete all parking lots
    response = client.get("/parking-lots/", headers=headers)
    if response.status_code == 200:
        for lot in response.json():
            try:
                client.delete(f"/parking-lots/{lot['id']}", headers=headers)
            except Exception as e:
                print(f"Warning: Could not delete parking lot {lot['id']}: {e}")

    # Create default parking lots if not testing create endpoints
    if "create" not in request.node.fspath.basename:
        lot = {
            "name": "Bedrijventerrein Almere Parkeergarage",
            "location": "Industrial Zone",
            "address": "Schanssingel 337, 2421 BS Almere",
            "capacity": 100,
            "tariff": 0.5,
            "daytariff": 0.5,
            "lat": 0,
            "lng": 0,
        }

        lot2 = {
            "name": "Vlaardingen Evenementenhal Parkeerterrein",
            "location": "Event Center",
            "address": "Westlindepark 756, 8920 AB Vlaardingen",
            "capacity": 50,
            "tariff": 0.5,
            "daytariff": 0.5,
            "lat": 0,
            "lng": 0,
        }

        client.post("/parking-lots", json=lot, headers=headers)
        client.post("/parking-lots", json=lot2, headers=headers)


# region HELPER FUNCTIONS FOR TESTS


def get_last_pid(client):
    """
    Gets the ID of the last parking lot in the database.
    Works with any number of parking lots (minimum 1).
    """
    response = client.get("/parking-lots/")

    if response.status_code != 200:
        pytest.fail(f"Failed to get parking lots: {response.status_code}")

    data = response.json()

    if not data or len(data) == 0:
        pytest.fail("No parking lots found in database")

    # Use -1 to get last item, works with both 1 and 2+ parking lots
    return data[-1]["id"]


def create_test_vehicle(client, headers, license_plate="TEST-VEHICLE"):
    """
    Creates a test vehicle for the authenticated user.

    Args:
        client: TestClient instance
        headers: Authorization headers with Bearer token
        license_plate: Unique license plate (default: "TEST-VEHICLE")

    Returns:
        int: The ID of the created vehicle

    Raises:
        pytest.fail: If vehicle creation fails
    """
    # Get authenticated user's ID
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
        error_detail = (
            create_response.json() if create_response.text else "No error details"
        )
        pytest.fail(
            f"Failed to create vehicle: {create_response.status_code} - {error_detail}"
        )

    # Get vehicle ID from GET /vehicles
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

    Args:
        client: TestClient instance
        headers: Authorization headers with Bearer token (must be superadmin)
        name: Name of the parking lot

    Returns:
        int: The ID of the created parking lot

    Raises:
        pytest.fail: If parking lot creation fails
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
        error_detail = (
            create_response.json() if create_response.text else "No error details"
        )
        pytest.fail(
            f"Failed to create parking lot: {create_response.status_code} - {error_detail}"
        )

    # Get the last parking lot ID
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

    Args:
        client_with_token: The client_with_token fixture
        role: User role ("user", "admin", "superadmin")
        vehicle_plate: License plate for the vehicle
        lot_name: Name for the parking lot

    Returns:
        tuple: (client, headers, vehicle_id, parking_lot_id)

    Example:
        client, headers, vehicle_id, lot_id = setup_reservation_prerequisites(client_with_token, "user")
    """
    # Get client with user role
    user_client, user_headers = client_with_token(role)

    # Create vehicle as user
    vehicle_id = create_test_vehicle(user_client, user_headers, vehicle_plate)

    # Get/create parking lot
    # Check if parking lots exist (from setup_parking_lots fixture)
    response = user_client.get("/parking-lots/")
    if response.status_code == 200 and response.json():
        # Use existing parking lot
        parking_lot_id = response.json()[-1]["id"]
    else:
        # Create new parking lot (requires superadmin)
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

    Args:
        client_with_token: The client_with_token fixture
        role: User role ("user", "admin", "superadmin")
        vehicle_plate: License plate for the vehicle

    Returns:
        tuple: (client, headers, vehicle_id, parking_lot_id)
    """
    return setup_reservation_prerequisites(
        client_with_token, role, vehicle_plate, "Session Test Lot"
    )
