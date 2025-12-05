from server import RequestHandler
from fastapi.testclient import TestClient

client = TestClient(RequestHandler)
vehicle_id = 1
BASE_URL = "http://localhost:8000"

# Test for if a vehicle gets deleted.
def delete_vehicle_delete_test():
    response = client.delete(f"{BASE_URL}/vehicles/delete/{vehicle_id}")
    assert response.status_code == 200