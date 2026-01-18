"""
this file contains all tests related to post parking lots endpoints.
"""


def test_create_parking_lot_with_superadmin(client_with_token):
    """Creates a new parking lot as a superadmin.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the parking lot is not created successfully or response data is invalid.
    """
    superadmin_client, headers = client_with_token("superadmin")
    fake_parking_lot = {
        "name": "Bedrijventerrein Almere Parkeergarage",
        "location": "Industrial Zone",
        "address": "Schanssingel 337, 2421 BS Almere",
        "capacity": 1,
        "tariff": 0.5,
        "daytariff": 0.5,
        "lat": 0,
        "lng": 0
    }

    response = superadmin_client.post("/parking-lots", json=fake_parking_lot, headers=headers)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Bedrijventerrein Almere Parkeergarage"


def test_create_parking_lot_with_admin(client_with_token):
    """Attempts to create a new parking lot as an admin user.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 403.
    """
    admin_client, headers = client_with_token("lotadmin")
    fake_parking_lot = {
        "name": "test",
        "location": "here",
        "address": "",
        "capacity": 1,
        "tariff": 0.5,
        "daytariff": 0.5,
        "lat": 0,
        "lng": 0
    }
    response = admin_client.post("/parking-lots", json=fake_parking_lot, headers=headers)
    assert response.status_code == 403


def test_create_parking_lot_with_user(client_with_token):
    """Attempts to create a new parking lot as a regular user.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 403.
    """
    user_client, headers = client_with_token("user")
    fake_parking_lot = {
        "name": "test",
        "location": "here",
        "address": "",
        "capacity": 1,
        "tariff": 0.5,
        "daytariff": 0.5,
        "lat": 0,
        "lng": 0
    }
    response = user_client.post("/parking-lots", json=fake_parking_lot, headers=headers)
    assert response.status_code == 403


def test_create_parking_lot_invalid_data(client_with_token):
    """Attempts to create a parking lot with invalid request data.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 400 or 422.
    """
    superadmin_client, headers = client_with_token("superadmin")
    invalid_data = "this should be invalid data"
    response = superadmin_client.post("/parking-lots", json=invalid_data, headers=headers)
    assert response.status_code in [400, 422]


def test_create_parking_lot_missing_required_fields(client_with_token):
    """Attempts to create a parking lot with missing required fields.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 400 or 422.
    """
    superadmin_client, headers = client_with_token("superadmin")
    incomplete_data = {
        "name": "Test Parking"
        # Missing location, capacity, etc.
    }
    response = superadmin_client.post("/parking-lots", json=incomplete_data, headers=headers)
    assert response.status_code in [400, 422]
