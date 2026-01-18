"""
this file contains all tests related to put parking lots endpoints.
"""

from datetime import datetime

import pytest
from api.tests.conftest import get_last_pid


@pytest.fixture
def valid_parking_lot_data():
    """
    Returns a valid parking lot.

    Returns:
        dict: A dictionary containing valid parking lot data used for update tests.
    """
    return {
        "name": "Bedrijventerrein Almere Parkeergarage",
        "location": "Industrial Zone",
        "address": "Schanssingel 337, 2421 BS Almere",
        "capacity": 1,
        "tariff": 0.5,
        "daytariff": 0.5,
        "lat": 0,
        "lng": 0
    }


# Tests voor PUT /parking-lots/{id}
def test_update_parking_lot_success(client_with_token, valid_parking_lot_data):
    """Tests successfully updating an existing parking lot.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.
        valid_parking_lot_data (dict): Valid parking lot data for the update request.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200 or response data is invalid.
    """
    superadmin_client, headers = client_with_token("superadmin")
    parking_lot_id = get_last_pid(superadmin_client)
    response = superadmin_client.put(
        f"/parking-lots/{parking_lot_id}",
        headers=headers,
        json=valid_parking_lot_data
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_update_parking_lot_not_found(client_with_token, valid_parking_lot_data):
    """Tests updating a non-existing parking lot.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.
        valid_parking_lot_data (dict): Valid parking lot data for the update request.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    superadmin_client, headers = client_with_token("superadmin")
    response = superadmin_client.put(
        "/parking-lots/999999",
        headers=headers,
        json=valid_parking_lot_data
    )
    assert response.status_code == 404


def test_update_parking_lot_unauthorized(client, valid_parking_lot_data):
    """Tests updating a parking lot without authentication.

    Args:
        client: Unauthenticated test client.
        valid_parking_lot_data (dict): Valid parking lot data for the update request.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
    parking_lot_id = get_last_pid(client)
    response = client.put(
        f"/parking-lots/{parking_lot_id}",
        json=valid_parking_lot_data
    )
    assert response.status_code == 401


def test_update_parking_lot_forbidden(client_with_token, valid_parking_lot_data):
    """Tests updating a parking lot with insufficient permissions.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.
        valid_parking_lot_data (dict): Valid parking lot data for the update request.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 403.
    """
    admin_client, headers = client_with_token("lotadmin")
    parking_lot_id = get_last_pid(admin_client)
    response = admin_client.put(
        f"/parking-lots/{parking_lot_id}",
        headers=headers,
        json=valid_parking_lot_data
    )
    assert response.status_code == 403


def test_update_parking_lot_invalid_data(client_with_token):
    """Tests updating a parking lot with invalid input data.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 400 or 422.
    """
    superadmin_client, headers = client_with_token("superadmin")
    parking_lot_id = get_last_pid(superadmin_client)
    invalid_data = {
        "capacity": "invalid_number",
        "tariff": -5.0,
        "name": ""
    }
    response = superadmin_client.put(
        f"/parking-lots/{parking_lot_id}",
        headers=headers,
        json=invalid_data
    )
    assert response.status_code in [400, 422]


def test_update_parking_lot_status_success(client_with_token):
    """Tests successfully updating the status of a parking lot.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200 or status is incorrect.
    """
    superadmin_client, headers = client_with_token("superadmin")
    pid = get_last_pid(superadmin_client)
    data = {
        "lid": pid,
        "lot_status": "closed",
        "closed_reason": "for testing",
        "closed_date": datetime.now().strftime("%Y-%m-%d")
    }
    response = superadmin_client.put(
        f"/parking-lots/{pid}/status",
        headers=headers,
        params=data
    )
    assert response.status_code == 200
    assert response.json()["new_status"] == "closed"


def test_update_parking_lot_status_forbidden(client_with_token):
    """Tests updating parking lot status with insufficient permissions.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 403.
    """
    user_client, headers = client_with_token("user")
    pid = get_last_pid(user_client)
    data = {
        "lid": pid,
        "lot_status": "closed",
        "closed_reason": "for testing",
        "closed_date": datetime.now().strftime("%Y-%m-%d")
    }
    response = user_client.put(
        f"/parking-lots/{pid}/status",
        headers=headers,
        params=data
    )
    assert response.status_code == 403


def test_update_parking_lot_status_unaothorized(client):
    """Tests updating parking lot status without authentication.

    Args:
        client: Unauthenticated test client.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
    pid = get_last_pid(client)
    data = {
        "lid": pid,
        "lot_status": "closed",
        "closed_reason": "for testing",
        "closed_date": datetime.now().strftime("%Y-%m-%d")
    }
    response = client.put(
        f"/parking-lots/{pid}/status",
        params=data
    )
    assert response.status_code == 401


def test_update_parking_lot_status_invalid_status(client_with_token):
    """Tests updating parking lot status with an invalid status value.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 400.
    """
    superadmin_client, headers = client_with_token("superadmin")
    pid = get_last_pid(superadmin_client)
    data = {
        "lid": pid,
        "lot_status": "invalid",
        "closed_reason": "for testing",
        "closed_date": datetime.now().strftime("%Y-%m-%d")
    }
    response = superadmin_client.put(
        f"/parking-lots/{pid}/status",
        headers=headers,
        params=data
    )
    assert response.status_code == 400


def test_update_parking_lot_status_no_closed_reason(client_with_token):
    """Tests updating parking lot status without providing a closed reason.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 400.
    """
    superadmin_client, headers = client_with_token("superadmin")
    pid = get_last_pid(superadmin_client)
    data = {
        "lid": pid,
        "lot_status": "closed",
        "closed_date": datetime.now().strftime("%Y-%m-%d")
    }
    response = superadmin_client.put(
        f"/parking-lots/{pid}/status",
        headers=headers,
        params=data
    )
    assert response.status_code == 400


def test_update_parking_lot_status_no_closed_date(client_with_token):
    """Tests updating parking lot status without providing a closed date.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200 or status is incorrect.
    """
    superadmin_client, headers = client_with_token("superadmin")
    pid = get_last_pid(superadmin_client)
    data = {
        "lid": pid,
        "lot_status": "closed",
        "closed_reason": "for testing",
    }
    response = superadmin_client.put(
        f"/parking-lots/{pid}/status",
        headers=headers,
        params=data
    )
    assert response.status_code == 200
    assert response.json()["new_status"] == "closed"


def test_update_parking_lot_increase_reserved_count_success(client_with_token):
    """Tests increasing and decreasing the reserved count of a parking lot.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the reserved count is not updated correctly.
    """
    superadmin_client, headers = client_with_token("superadmin")
    lid = get_last_pid(superadmin_client)
    response = superadmin_client.get(f"/parking-lots/{lid}")
    current_reserved = response.json()["reserved"]

    data = {
        "lid": lid,
        "action": "increase"
    }
    _ = superadmin_client.put(
        f"/parking-lots/{lid}/reserved",
        headers=headers,
        params=data
    )
    assert response.status_code == 200
    response = superadmin_client.get(f"/parking-lots/{lid}")
    assert response.json()["reserved"] == current_reserved + 1

    data = {
        "lid": lid,
        "action": "decrease"
    }
    _ = superadmin_client.put(
        f"/parking-lots/{lid}/reserved",
        headers=headers,
        params=data
    )
    assert response.status_code == 200
    response = superadmin_client.get(f"/parking-lots/{lid}")
    assert response.json()["reserved"] == current_reserved
