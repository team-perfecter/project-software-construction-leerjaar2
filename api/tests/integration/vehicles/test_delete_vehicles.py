import pytest
from api.tests.conftest import get_last_vid


# Test dat een gebruiker zijn eigen vehicle kan verwijderen
@pytest.mark.asyncio
def test_delete_vehicle_success(client_with_token):
    client, headers = client_with_token("superadmin")

    vehicle_id = get_last_vid(client_with_token)

    response = client.delete(
        f"/vehicles/delete/{vehicle_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Vehicle succesfully deleted"

    
# Test verwijderen van een niet-bestaand vehicle
@pytest.mark.asyncio
def test_delete_vehicle_not_found(client_with_token):
    client, headers = client_with_token("superadmin")

    response = client.delete(
        "/vehicles/delete/999999",
        headers=headers,
    )

    assert response.status_code == 404


# Test dat een niet-ingelogde gebruiker geen vehicle kan verwijderen
@pytest.mark.asyncio
def test_delete_vehicle_unauthorized(client):

    response = client.delete("/vehicles/delete/1")
    assert response.status_code == 401


# Test dat een ingelogde gebruiker zijn vehicle kan verwijderen
def test_delete_vehicle_success(client_with_token):
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)

    response = client.delete(f"/vehicles/delete/{vehicle_id}", headers=headers)
    assert response.status_code == 200


# Test wat er gebeurt als de gebruiker niet is ingelogd
def test_delete_vehicle_not_logged_in(client):

    response = client.delete("/vehicles/delete/1")
    assert response.status_code == 401


# Test wat er gebeurt als het voertuig niet bestaat
def test_delete_vehicle_not_found(client_with_token):
    client, headers = client_with_token("superadmin")

    response = client.delete("/vehicles/delete/999999", headers=headers)
    assert response.status_code == 404


# Test wat er gebeurt als een gebruiker een voertuig probeert te verwijderen die niet van hem is
def test_delete_vehicle_unauthorized(client_with_token):
    client, headers = client_with_token("user")

    response = client.delete("/vehicles/delete/1", headers=headers)
    assert response.status_code == 404