"""
This file sets up the data required for running each test. 
It also contains fixtures that provide clients to communicate with the API.
"""

from json import JSONDecodeError
import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.auth_utils import create_access_token
from api.models.user_model import UserModel

PYTEST_PLUGINS = "pytest_benchmark"


def pytest_configure(config):
    """
    Configure pytest benchmark plugin to use a minimum of 20 rounds for benchmarking tests.
    """
    config.option.benchmark_min_rounds = 20

def run_fixture_on_test(filters, request) -> bool:
    """
    A filter for the setup fixtures.
    only continues fixtures if the filename passes the filter.
    this improves performance for the tests.
    
    filters: The names of the files the fixture should run in
    """
    can_continue = False
    for f in filters:
        if f in request.node.fspath.basename.lower():
            can_continue = True
            break
    return can_continue

@pytest.fixture(scope="session", name="client")
def test_client():
    """
    Provides a FastAPI TestClient instance for making HTTP requests without authentication.
    
    Returns:
        TestClient: FastAPI test client instance.
    """
    return TestClient(app)


@pytest.fixture(scope="session", name="client_with_token")
def test_client_with_token(client):
    """
    Provides a TestClient instance along 
    with headers containing a JWT token for a specified user role.
    
    Usage:
        client, headers = client_with_token("superadmin")
        client, headers = client_with_token("paymentadmin")
    
    Args:
        client (TestClient): The un-authenticated FastAPI test client.
    
    Returns:
        function: A helper function that accepts a username and returns (client, headers).
    """
    def _client_with_role(username: str):
        """
        Generate headers with JWT token for the given username.
        
        Args:
            username (str): The username for which the token is generated.
        
        Returns:
            Tuple[TestClient, dict]: Test client and headers with Authorization token.
        """
        token = create_access_token({"sub": username})
        headers = {"Authorization": f"Bearer {token}"}
        return client, headers

    return _client_with_role


@pytest.fixture(scope="session", autouse=True)
def seed_all_data(client_with_token):
    """
    Seed all required data once per test session before any tests run.
    Calls other seeding functions for vehicles, users, parking lots, payments, etc.
    """

    client, headers = client_with_token("superadmin")

    seed_vehicles(client, headers, True)

    seed_users(client, headers, True)

    seed_parking_lots(client, headers, True)

    seed_payments(client, headers, True)


def seed_vehicles(client, headers, create_default):
    """
    Seeds data for payments.
    """
    # Get all vehicles
    response = client.get("/vehicles", headers=headers)
    try:
        data = response.json()
    except JSONDecodeError:
        data = []

    # Ensure vehicles_list is a list
    if isinstance(data, dict):
        vehicles_list = []
    elif isinstance(data, list):
        vehicles_list = data
    else:
        vehicles_list = []

    # Delete all existing vehicles
    for vehicle in vehicles_list:
        if isinstance(vehicle, dict) and "id" in vehicle:
            client.delete(f"/vehicles/delete/{vehicle['id']}", headers=headers)

    # Seed a default vehicle if not testing creation
    #if "create" not in request.node.fspath.basename:
    if create_default:
        vehicle = {
            "user_id": 1,
            "license_plate": "ABC123",
            "make": "Toyota",
            "model": "Corolla",
            "color": "Blue",
            "year": 2020,
        }
        client.post("/vehicles/create", json=vehicle, headers=headers)

def seed_users(client, headers, create_default):
    """
    Seeds data for payments.
    """
    response = client.get("/users/", headers=headers)

    if create_default:
        # Delete users with id > 4
        for user in response.json():
            if user['id'] > 4:
                client.delete(f"/users/{user['id']}", headers=headers)

        # Seed default users
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

def seed_parking_lots(client, headers, create_default):
    """
    Seeds data for payments.
    """
    response = client.get("/parking-lots/", headers=headers)
    if response.status_code == 200:
        for lot in response.json():
            client.delete(f"/parking-lots/{lot['id']}", headers=headers)

    if create_default:
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

def seed_payments(client, headers, create_default):
    """
    Seeds data for payments.
    """
    user_model = UserModel()

    # Ensure superadmin exists
    user = user_model.get_user_by_username("superadmin")
    if not user:
        raise RuntimeError("Superadmin must exist in the DB")
    # Delete all payments for superadmin
    response = client.get("/payments/me", headers=headers)
    if response.status_code == 200:
        for payment in response.json():
            client.delete(f"/payments/{payment['id']}", headers=headers)

    # Seed 5 payments if not testing creation
    if create_default:
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

@pytest.fixture(autouse=True)
def setup_vehicles(request, client_with_token):
    """
    Fixture to clear all vehicles before each test and optionally seed a default vehicle.
    
    If the test filename contains "create", no vehicle is seeded. 
    Otherwise, one default vehicle is added.
    
    Args:
        request: pytest request object.
        client_with_token: Fixture that returns a client with JWT headers.
    """
    if not run_fixture_on_test(["vehicles"], request):
        return
    client, headers = client_with_token("superadmin")
    create_default = "create" not in request.node.fspath.basename
    seed_vehicles(client, headers, create_default)



@pytest.fixture(autouse=True)
def setup_users(request, client_with_token):
    """
    Fixture to clear all users above the system default users.
    Seeds 4 default users if the test is not a creation test.
    
    Args:
        request: pytest request object.
        client_with_token: Fixture that returns a client with JWT headers.
    """
    if not run_fixture_on_test(["user"], request):
        return
    client, headers = client_with_token("superadmin")
    create_default = "create" not in request.node.fspath.basename
    seed_users(client, headers, create_default)


@pytest.fixture(autouse=True)
def setup_parking_lots(request, client_with_token):
    """
    Fixture to clear all parking lots before each test.
    Adds two default parking lots unless testing creation endpoints.
    
    Args:
        request: pytest request object.
        client_with_token: Fixture that returns a client with JWT headers.
    """
    if not run_fixture_on_test(["parking_lot"], request):
        return
    client, headers = client_with_token("superadmin")
    create_default = "create" not in request.node.fspath.basename
    seed_parking_lots(client, headers, create_default)


@pytest.fixture(autouse=True)
def setup_payments(request, client_with_token):
    """
    Fixture to clear all payments for superadmin,
    and seed 5 payments if not testing creation endpoints.
    
    Args:
        request: pytest request object.
        client_with_token: Fixture that returns a client with JWT headers.
    """
    if not run_fixture_on_test(["payments"], request):
        return
    client, headers = client_with_token("superadmin")
    create_default = "create" not in request.node.fspath.basename
    seed_payments(client, headers, create_default)


def get_last_pid(client):
    """
    Returns the ID of the last parking lot in the database.

    Args:
        client (TestClient): FastAPI test client.

    Returns:
        int: ID of the last parking lot.
    """
    response = client.get("/parking-lots/")
    data = response.json()
    return data[-1]["id"]


def get_last_payment_id(client_with_token):
    """
    Returns the ID of the last payment for superadmin.
    
    Args:
        client_with_token: Fixture that returns a client with JWT headers.
    
    Returns:
        int: ID of the last payment.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/payments/me", headers=headers)
    data = response.json()
    return data[-1]["id"]


def get_last_uid(client_with_token):
    """
    Returns the ID of the last user in the database.
    
    Args:
        client_with_token: Fixture that returns a client with JWT headers.
    
    Returns:
        int: ID of the last user.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/users/", headers=headers)
    data = response.json()
    return data[-1]["id"]


def get_last_vid(client_with_token):
    """
    Returns the ID of the last vehicle in the database.
    
    Args:
        client_with_token: Fixture that returns a client with JWT headers.
    
    Returns:
        int: ID of the last vehicle.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/vehicles", headers=headers)
    data = response.json()
    return data[-1]["id"]