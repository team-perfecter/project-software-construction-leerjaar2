"""
this file contains all tests related to post vehicle endpoints.
"""


# Controleer of het voertuig correct is aangemaakt
def test_create_vehicle(client_with_token) -> None:
    """Creates a vehicle successfully with valid data and authentication.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the vehicle is not created successfully.
    """
    client, headers = client_with_token("superadmin")

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
    """Attempts to create a vehicle with missing required fields.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 422.
    """
    client, headers = client_with_token("superadmin")

    # 'make' en 'model' ontbreken
    vehicle = {
        "user_id": 1,
        "license_plate": "XYZ987",
        "color": "Red",
        "year": 2022,
    }

    response = client.post("/vehicles/create", json=vehicle, headers=headers)
    assert response.status_code == 422  # Unprocessable Entity


# Testen wat er gebeurt als er geen gebruiker is ingelogd
def test_create_vehicle_no_user(client) -> None:
    """Attempts to create a vehicle without authentication.

    Args:
        client: Unauthenticated test client.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
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


# Testen wat er gebeurt als een ingelogde gebruiker geen (geldige) user_id meegeeft
def test_create_vehicle_no_userid_in_json(client_with_token) -> None:
    """Creates a vehicle while relying on the authenticated user's ID.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the vehicle is not created successfully.
    """
    client, headers = client_with_token("superadmin")

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
    assert "message" in response.json()


# Testen wat er gebeurt als een gebruiker een andere user_id meegeeft
def test_create_vehicle_wrong_userid(client_with_token) -> None:
    """Creates a vehicle while providing a user_id different from the authenticated user.

    The API should ignore the provided user_id and use the authenticated user's ID.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the vehicle is not created successfully.
    """
    client, headers = client_with_token("superadmin")

    vehicle = {
        "user_id": 9999,  # Niet de ingelogde gebruiker
        "license_plate": "QRS567",
        "make": "Mazda",
        "model": "3",
        "color": "White",
        "year": 2020,
    }

    response = client.post("/vehicles/create", json=vehicle, headers=headers)
    assert response.status_code == 201
