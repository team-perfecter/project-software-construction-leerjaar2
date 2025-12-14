import pytest
from api.tests.conftest import get_last_vid


# Test dat een gebruiker zijn eigen vehicle succesvol kan updaten
@pytest.mark.asyncio
def test_update_vehicle_success(client_with_token):
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client, headers)
    updated_vehicle = {
        "license_plate": "UPDATED123",
        "make": "Tesla",
        "model": "Model 3",
        "color": "Red",
        "year": 2024,
    }

    response = client.put(
        f"/vehicles/update/{vehicle_id}",
        json=updated_vehicle,
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Vehicle succesfully updated"

# Test update van een niet-bestaand vehicle
@pytest.mark.asyncio
def test_update_vehicle_not_found(client_with_token):
    client, headers = client_with_token("superadmin")

    updated_vehicle = {
        "license_plate": "DOESNOTEXIST",
        "make": "BMW",
        "model": "X5",
        "color": "Black",
        "year": 2022,
    }

    response = client.put(
        "/vehicles/update/999999",
        json=updated_vehicle,
        headers=headers,
    )

    assert response.status_code == 404

# Test dat een niet-ingelogde gebruiker geen vehicle kan updaten
@pytest.mark.asyncio
def test_update_vehicle_unauthorized(client):
    updated_vehicle = {
        "license_plate": "NOAUTH",
        "make": "Ford",
        "model": "Focus",
        "color": "Blue",
        "year": 2020,
    }

    response = client.put(
        "/vehicles/update/1",
        json=updated_vehicle,
    )

    assert response.status_code == 401


# Test wat er gebeurt als de gebruiker niet is ingelogd
def test_update_vehicle_not_logged_in(client):

    response = client.put("/vehicles/update/1", json={})
    assert response.status_code == 401

# Test wat er gebeurt als het voertuig niet bestaat
def test_update_vehicle_not_found(client_with_token):
    client, headers = client_with_token("superadmin")

    update_data = {
        "license_plate": "XXX999",
        "make": "Ford",
        "model": "Focus",
        "color": "Red",
        "year": 2020,
    }

    response = client.put("/vehicles/update/999999", json=update_data, headers=headers)
    assert response.status_code == 404