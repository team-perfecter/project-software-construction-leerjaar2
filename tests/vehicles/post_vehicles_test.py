from server import RequestHandler
from fastapi.testclient import TestClient

client = TestClient(RequestHandler)
vehicle_id = 1
BASE_URL = "http://localhost:8000"

# Test for if a vehicle gets created.
def post_vehicle_create_test():
    response = client.post(f"{BASE_URL}/vehicles/create")
    assert response.status_code == 200