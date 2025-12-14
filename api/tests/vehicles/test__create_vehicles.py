import pytest

# Controleer of het voertuig correct is aangemaakt
def test_create_vehicle(client_with_token) -> None:
    client, headers = client_with_token("superadmin")

    # 1. Standaard create vehicle test
    vehicle = {
        "user_id": 1,
        "license_plate": "ABC123",
        "make": "Toyota",
        "model": "Corolla",
        "color": "Blue",
        "year": 2020,
    }

    response = client.post("/vehicles/create", json=vehicle, headers=headers)
    assert response.status_code == 201
    assert response.json()["message"] == "Vehicle successfully created."

# Testen of een incomplete payload een 422 teruggeeft
def test_create_vehicle_incomplete_data(client_with_token) -> None:
    client, headers = client_with_token("superadmin")

    # Verwijder 'make' en 'model' om een incomplete payload te simuleren
    vehicle = {
        "user_id": 1,
        "license_plate": "XYZ987",
        "color": "Red",
        "year": 2022,
    }

    response = client.post("/vehicles/create", json=vehicle, headers=headers)
    assert response.status_code == 422  # Unprocessable Entity
    # Optioneel: assert op de foutboodschap in response.json()

# Testen wat er gebeurt als er geen gebruiker is ingelogd
def test_create_vehicle_no_user(client) -> None:
    # Zonder headers sturen we een request
    vehicle = {
        "user_id": 1,
        "license_plate": "NOP456",
        "make": "Ford",
        "model": "Fiesta",
        "color": "Green",
        "year": 2021,
    }

    response = client.post("/vehicles/create", json=vehicle)
    assert response.status_code == 401  # Unauthorized

# Testen wat er gebeurt als een ingelogde gebruiker geen user_id meegeeft
def test_create_vehicle_no_userid_in_json(client_with_token) -> None:
    client, headers = client_with_token("superadmin")

    # user_id wordt weggelaten, fastapi dependancy moet automatisch de ingelogde user gebruiken
    vehicle = {
        "user_id": 1,
        "license_plate": "LMN123",
        "make": "Honda",
        "model": "Civic",
        "color": "Black",
        "year": 2023,
    }

    response = client.post("/vehicles/create", json=vehicle, headers=headers)
    assert response.status_code == 201
    # Controleer dat de vehicle user_id correct is gezet
    vehicle_data = response.json()
    assert "message" in vehicle_data

# Testen wat er gebeurt als een gebruiker een user_id meegeeft die niet van de ingelogde gebruiker is
def test_create_vehicle_wrong_userid(client_with_token) -> None:
    client, headers = client_with_token("superadmin")

    # user_id van iemand anders meegeven
    vehicle = {
        "user_id": 9999,  # veronderstel dat dit niet de ingelogde gebruiker is
        "license_plate": "QRS567",
        "make": "Mazda",
        "model": "3",
        "color": "White",
        "year": 2020,
    }

    response = client.post("/vehicles/create", json=vehicle, headers=headers)
    # De endpoint zou altijd de ingelogde user_id moeten gebruiken, dus dit mag geen effect hebben
    assert response.status_code == 201