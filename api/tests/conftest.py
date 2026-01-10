import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.auth_utils import create_access_token
from api.models.user_model import UserModel



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
            if user['id'] > 4:
                client.delete(f"/users/{user['id']}", headers=headers)

        user2 = {
            "username": "lotadmin",
            "password": "admin123",
            "email": "bla@bla.com",
            "name": "lotadmin",
            "role": "lotadmin"
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

@pytest.fixture(autouse=True)
def setup_parking_lots(request, client_with_token):
    """
    Clears the database of parking lots.
    If the create endpoints are not being tested, this also adds 2 parking lots to the database
    """

    client, headers = client_with_token("superadmin")
    response = client.get("/parking-lots/", headers=headers)
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
            lid = get_last_pid(client)
            payment = {
                "user_id": user.id,
                "parking_lot_id": f"{lid}",
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
