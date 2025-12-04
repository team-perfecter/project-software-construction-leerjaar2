from fastapi.testclient import TestClient
from api.main import app
from api.tests.conftest import get_last_pid

client = TestClient(app)

# Tests voor DELETE /parking-lots/{id}
def test_delete_parking_lot_success(client_with_token):
    """Test: DELETE /parking-lots/{id} - Succesvol verwijderen parking lot"""
    client, headers = client_with_token("superadmin")
    parking_lot_id = get_last_pid(client)
    response = client.delete(f"/parking-lots/{parking_lot_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)

def test_delete_parking_lot_not_found(client_with_token):
    """Test: DELETE /parking-lots/{id} - Niet bestaande parking lot"""
    client, headers = client_with_token("superadmin")
    response = client.delete(f"/parking-lots/999999", headers=headers)
    assert response.status_code == 404

def test_delete_parking_lot_unauthorized():
    """Test: DELETE /parking-lots/{id} - Zonder authenticatie"""
    parking_lot_id = get_last_pid(client)
    response = client.delete(f"/parking-lots/{parking_lot_id}")
    assert response.status_code == 401

def test_delete_parking_lot_forbidden(client_with_token):
    """Test: DELETE /parking-lots/{id} - Normale user toegang geweigerd"""
    client, headers = client_with_token("user")
    parking_lot_id = get_last_pid(client)
    response = client.delete(f"/parking-lots/{parking_lot_id}", headers=headers)
    assert response.status_code == 403

def test_delete_parking_lot_invalid_id(client_with_token):
    """Test: DELETE /parking-lots/{id} - Ongeldige ID format"""
    client, headers = client_with_token("superadmin")
    invalid_id = "abc"
    response = client.delete(f"/parking-lots/{invalid_id}", headers=headers)
    assert response.status_code in [400, 404, 422]