import sys
from server import RequestHandler
from fastapi.testclient import TestClient

client = TestClient(RequestHandler)
vehicle_id = 1
BASE_URL = "http://localhost:8000"

# Test for getting all vehicles.
def get_vehicles_test():
    response = client.get(f"{BASE_URL}/vehicles")
    assert response.status_code == 200
    vehicle_data = [{
        {
            "id": "1",
            "user_id": "1",
            "license_plate": "76-KQQ-7",
            "make": "Peugeot",
            "model": "308",
            "color": "Brown",
            "year": 2024,
            "created_at": "2024-08-13"
        },
        {
            "id": "2",
            "user_id": "2",
            "license_plate": "57-RCX-5",
            "make": "SEAT",
            "model": "Toledo",
            "color": "Blue",
            "year": 2022,
            "created_at": "2022-09-13"
        },
    }]
    assert vehicle_data

# Test for getting all vehicles of a user.
def get_vehicle_user_test():
    response = client.get(f"{BASE_URL}/vehicles/user")
    assert response.status_code == 200

# Test for getting the reservations of a vehicle.
def get_vehicle_reservation_test():
    response = client.get(f"{BASE_URL}/vehicles/reservations/{vehicle_id}")
    assert response.status_code == 200

# Test for getting the history of a vehicle.
def get_vehicle_history_test():
    response = client.get(f"{BASE_URL}/vehicles/history/{vehicle_id}")
    assert response.status_code == 200