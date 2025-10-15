from server import RequestHandler
from fastapi.testclient import TestClient

client = TestClient(RequestHandler)
vehicle_id = 1
BASE_URL = "http://localhost:8000"

# Test for if a vehicle gets updated.
def put_vehicle_update_test():
    response = client.put(f"{BASE_URL}/vehicles/update/{vehicle_id}")
    assert response.status_code == 200