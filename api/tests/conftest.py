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

    # Clears all parking lots
    client, headers = client_with_token("superadmin")
    response = client.get("/parking-lots/", headers=headers)
    if response.status_code == 200:
        for lot in response.json():
            client.delete(f"/parking-lots/{lot['id']}", headers=headers)

    if "create" not in request.node.fspath.basename:
        # Creates 2 parking lots if the create endpoints are not being tested
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
    There are a max of 2 parking lots in the database when running a new test.
    The id of these parking lots might be different for each test.
    this function gets the 2 parking lots, and returns the id of the last one.
    this is to make sure the id of a parking lot that is being tested actually exists.
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
