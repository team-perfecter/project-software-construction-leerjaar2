import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.auth_utils import create_access_token
from api.models.user_model import UserModel
from datetime import datetime, timedelta


pytest_plugins = "pytest_benchmark"


def pytest_configure(config):
    config.option.benchmark_min_rounds = 20


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
def cleanup_database_order(request, client_with_token):
    """
    Ensures database cleanup happens AFTER test in correct order.
    Order: reservations -> vehicles -> parking_lots -> users
    """
    # Geen cleanup VOOR test
    yield  # Test runs here

    # Cleanup NA test in reverse order of dependencies
    client, headers = client_with_token("superadmin")

    try:
        # 1. Delete ALL reservations first
        reservations_response = client.get("/admin/reservations", headers=headers)
        if reservations_response.status_code == 200:
            reservations = reservations_response.json()
            if isinstance(reservations, list):
                for reservation in reservations:
                    if isinstance(reservation, dict) and "id" in reservation:
                        client.delete(
                            f"/admin/reservations/{reservation['id']}", headers=headers
                        )

        # 2. Then delete vehicles
        vehicles_response = client.get("/vehicles", headers=headers)
        if vehicles_response.status_code == 200:
            vehicles = vehicles_response.json()
            if isinstance(vehicles, list):
                for vehicle in vehicles:
                    if isinstance(vehicle, dict) and "id" in vehicle:
                        client.delete(
                            f"/vehicles/delete/{vehicle['id']}", headers=headers
                        )

        # 3. Then delete parking lots
        parking_response = client.get("/parking-lots/", headers=headers)
        if parking_response.status_code == 200:
            parking_lots = parking_response.json()
            if isinstance(parking_lots, list):
                for lot in parking_lots:
                    if isinstance(lot, dict) and "id" in lot:
                        client.delete(f"/parking-lots/{lot['id']}", headers=headers)

    except Exception as e:
        print(f"Cleanup error: {e}")


@pytest.fixture(autouse=True)
def setup_parking_lots(request, client_with_token):
    """
    Clears the database of parking lots BEFORE test.
    If the create endpoints are not being tested, this also adds 2 parking lots to the database
    """
    client, headers = client_with_token("superadmin")

    # Delete all reservations FIRST (to avoid foreign key constraint)
    try:
        reservations_response = client.get("/admin/reservations", headers=headers)
        if reservations_response.status_code == 200:
            reservations = reservations_response.json()
            if isinstance(reservations, list):
                for reservation in reservations:
                    if isinstance(reservation, dict) and "id" in reservation:
                        client.delete(
                            f"/admin/reservations/{reservation['id']}", headers=headers
                        )
    except Exception:
        pass

    # Now delete parking lots
    response = client.get("/parking-lots/", headers=headers)
    if response.status_code == 200:
        for lot in response.json():
            client.delete(f"/parking-lots/{lot['id']}", headers=headers)

    # Add default parking lots if NOT testing creation
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


@pytest.fixture(autouse=True)
def setup_vehicles(request, client_with_token):
    """Always creates 2 vehicles before each test"""
    client, headers = client_with_token("superadmin")
    client_user, headers_user = client_with_token("user")

    # Clean up first
    try:
        vehicles_response = client.get("/vehicles", headers=headers)
        if vehicles_response.status_code == 200:
            vehicles = vehicles_response.json()
            if isinstance(vehicles, list):
                for veh in vehicles:
                    if isinstance(veh, dict) and "id" in veh:
                        client.delete(
                            f"/vehicles/delete/{veh['id']}", headers=headers
                        )
    except Exception as e:
        print(f"Cleanup vehicles error: {e}")
        pass

    # Always create default vehicles
    vehicle1 = {
        "license_plate": "TEST-001",
        "make": "Toyota",
        "model": "Corolla",
        "color": "Blue",
        "year": 2020
    }
    
    vehicle2 = {
        "license_plate": "TEST-002",
        "make": "Honda",
        "model": "Civic",
        "color": "Red",
        "year": 2021
    }
    
    response1 = client.post("/vehicles/create", json=vehicle1, headers=headers)
    print(f"[DEBUG] Vehicle 1 creation: {response1.status_code}")
    if response1.status_code != 201:
        print(f"[DEBUG] Vehicle 1 error: {response1.text}")
    
    response2 = client_user.post("/vehicles/create", json=vehicle2, headers=headers_user)
    print(f"[DEBUG] Vehicle 2 creation: {response2.status_code}")
    if response2.status_code != 201:
        print(f"[DEBUG] Vehicle 2 error: {response2.text}")
    
    check_response = client.get("/vehicles", headers=headers)
    print(f"[DEBUG] After creation, vehicles status: {check_response.status_code}")
    if check_response.status_code == 200:
        print(f"[DEBUG] Vehicles count: {len(check_response.json())}")


@pytest.fixture(autouse=True)
def setup_reservations(request, client_with_token):
    """
    Clears the database of reservations before each test.
    If the test is not testing reservation creation, it also adds a default reservation.
    """
    client, headers = client_with_token("superadmin")

    # Delete existing reservations
    response = client.get("/admin/reservations", headers=headers)
    if response.status_code == 200:
        try:
            reservations = response.json()
            if isinstance(reservations, list):
                for reservation in reservations:
                    if isinstance(reservation, dict) and "id" in reservation:
                        client.delete(
                            f"/admin/reservations/{reservation['id']}", headers=headers
                        )
        except Exception:
            pass

    # Add default reservation if not testing creation
    if "create" not in request.node.fspath.basename:
        vehicle_response = client.get("/vehicles", headers=headers)
        parking_response = client.get("/parking-lots/", headers=headers)

        if (
            vehicle_response.status_code == 200
            and vehicle_response.json()
            and parking_response.status_code == 200
            and parking_response.json()
        ):
            vehicles = vehicle_response.json()
            parking_lots = parking_response.json()

            # Check if we have data
            if len(vehicles) > 0 and len(parking_lots) > 0:
                vehicle_id = vehicles[0]["id"]
                parking_lot_id = parking_lots[0]["id"]
                user_id = 1  # superadmin id

                reservation = {
                    "user_id": user_id,
                    "parking_lot_id": parking_lot_id,
                    "vehicle_id": vehicle_id,
                    "start_date": (datetime.now() + timedelta(days=3)).isoformat(),
                    "end_date": (datetime.now() + timedelta(days=4)).isoformat(),
                }

                client.post("/admin/reservations", json=reservation, headers=headers)


def get_last_pid(client):
    """
    Returns the id of the last parking lot.
    """
    response = client.get("/parking-lots/")
    data = response.json()
    return data[-1]["id"]


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
            if user["id"] > 4:
                client.delete(f"/users/{user['id']}", headers=headers)

        user2 = {
            "username": "admin",
            "password": "admin123",
            "email": "bla@bla.com",
            "name": "admin",
            "role": "admin",
        }

        user3 = {
            "username": "paymentadmin",
            "password": "admin123",
            "email": "bla@bla.com",
            "name": "paymentadmin",
            "role": "paymentadmin",
        }

        user4 = {
            "username": "user",
            "password": "admin123",
            "email": "bla@bla.com",
            "name": "user",
            "role": "user",
        }

        user5 = {
            "username": "extrauser",
            "password": "admin123",
            "email": "bla@bla.com",
            "name": "extrauser",
            "role": "user",
        }

        client.post("/create_user", json=user2, headers=headers)
        client.post("/create_user", json=user3, headers=headers)
        client.post("/create_user", json=user4, headers=headers)
        client.post("/create_user", json=user5, headers=headers)


def get_last_reservation_id(client_with_token):
    """
    Returns the ID of the last reservation.
    Useful to make sure the reservation you test exists.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/admin/reservations", headers=headers)

    if response.status_code == 200:
        for lot in response.json():
            client.delete(f"/parking-lots/{lot['id']}/force", headers=headers)

    if "create" not in request.node.fspath.basename:
        lot = {
            "name": "Bedrijventerrein Almere Parkeergarage",
            "location": "Industrial Zone",
            "address": "Schanssingel 337, 2421 BS Almere",
            "capacity": 100,
            "tariff": 0.5,
            "daytariff": 0.5,
            "lat": 0,
            "lng": 0
        }

        lot2 = {
            "name": "Vlaardingen Evenementenhal Parkeerterrein",
            "location": "Event Center",
            "address": "Westlindepark 756, 8920 AB Vlaardingen",
            "capacity": 50,
            "tariff": 0.5,
            "daytariff": 0.5,
            "lat": 0,
            "lng": 0
        }

        client.post("/parking-lots", json=lot, headers=headers)
        client.post("/parking-lots", json=lot2, headers=headers)


def get_last_pid(client):
    """
    Returns the id of the last parking lot.
    """
    response = client.get("/parking-lots/")
    data = response.json()
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
                "bank": f"bank{i+1}",
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
