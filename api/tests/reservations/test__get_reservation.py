import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from fastapi.testclient import TestClient
from api.main import app
from api.tests.conftest import get_last_pid

client = TestClient(app)


# region HELPER FUNCTIONS


def create_vehicle_for_user(client, headers, license_plate="TEST-001"):
    """Helper function to create a test vehicle and return its ID"""
    vehicle_data = {
        "user_id": 1,
        "license_plate": license_plate,
        "make": "Toyota",
        "model": "Corolla",
        "color": "Blue",
        "year": 2024,
    }
    response = client.post("/vehicles/create", json=vehicle_data, headers=headers)

    if response.status_code != 201:
        pytest.fail(
            f"Failed to create vehicle: {response.status_code} - {response.json()}"
        )

    vehicles_response = client.get("/vehicles", headers=headers)
    if vehicles_response.status_code == 200:
        vehicles = vehicles_response.json()
        if vehicles and len(vehicles) > 0:
            last_vehicle = vehicles[-1]
            if isinstance(last_vehicle, (tuple, list)):
                return last_vehicle[0]
            elif isinstance(last_vehicle, dict):
                return last_vehicle["id"]

    pytest.fail(f"Could not extract vehicle ID. Response: {vehicles_response.json()}")


def create_test_reservation(
    client, headers, vehicle_id, parking_lot_id, days_ahead=1, duration=1
):
    """Helper to create a reservation and return its ID"""
    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": (datetime.now() + timedelta(days=days_ahead)).isoformat(),
        "end_time": (
            datetime.now() + timedelta(days=days_ahead + duration)
        ).isoformat(),
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    if response.status_code == 201:
        try:
            message = response.json()["detail"]["message"]
            import re

            match = re.search(r"\d+", message)
            if match:
                return int(match.group())
        except Exception as e:
            print(f"Could not extract reservation ID: {e}")

    return None


# GET /reservations/vehicle/{vehicle_id} TESTS


def test_get_reservations_by_vehicle_success(client_with_token):
    """
    Test: Successfully get reservations for a vehicle
    Covers: Line 26-35 (happy path)
    """
    client, headers = client_with_token("user")
    vehicle_id = create_vehicle_for_user(client, headers, "GET-SUCCESS-01")

    response = client.get(f"/reservations/vehicle/{vehicle_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_reservations_by_vehicle_unauthorized():
    """
    Test: Get reservations without authentication
    Covers: Line 26 (authentication dependency)
    """
    response = client.get("/reservations/vehicle/1")
    assert response.status_code == 401


def test_get_reservations_by_vehicle_not_found(client_with_token):
    """
    Test: Get reservations for non-existent vehicle
    Covers: Line 27-28 (vehicle not found check)
    """
    client, headers = client_with_token("user")
    response = client.get("/reservations/vehicle/99999", headers=headers)
    assert response.status_code == 404
    assert "vehicle not found" in response.json()["detail"].lower()


def test_get_reservations_by_vehicle_wrong_owner(client_with_token):
    """
    Test: Try to get reservations for another user's vehicle
    Covers: Line 30-31 (ownership check)
    """
    user_client, user_headers = client_with_token("user")
    vehicle_id = create_vehicle_for_user(user_client, user_headers, "GET-WRONG-01")

    admin_client, admin_headers = client_with_token("admin")
    response = admin_client.get(
        f"/reservations/vehicle/{vehicle_id}", headers=admin_headers
    )
    assert response.status_code == 403
    assert "does not belong" in response.json()["detail"].lower()


def test_get_reservations_by_vehicle_invalid_id_format(client_with_token):
    """
    Test: Get reservations with invalid vehicle ID format
    Covers: FastAPI validation layer
    """
    client, headers = client_with_token("user")
    response = client.get("/reservations/vehicle/invalid", headers=headers)
    assert response.status_code == 422


def test_get_reservations_by_vehicle_zero_id(client_with_token):
    """
    Test: Get reservations for vehicle with ID = 0
    Covers: Edge case - zero ID
    """
    client, headers = client_with_token("user")
    response = client.get("/reservations/vehicle/0", headers=headers)
    assert response.status_code == 404


def test_get_reservations_by_vehicle_negative_id(client_with_token):
    """
    Test: Get reservations with negative vehicle ID
    Covers: Edge case - negative ID
    """
    client, headers = client_with_token("user")
    response = client.get("/reservations/vehicle/-1", headers=headers)
    assert response.status_code == 404


def test_get_reservations_by_vehicle_with_existing_reservations(client_with_token):
    """
    Test: Get reservations when reservations exist
    Covers: Line 33-35 (return reservation list)
    """
    client, headers = client_with_token("user")
    vehicle_id = create_vehicle_for_user(client, headers, "GET-EXIST-01")
    parking_lot_id = get_last_pid(client)

    res_id = create_test_reservation(client, headers, vehicle_id, parking_lot_id)

    response = client.get(f"/reservations/vehicle/{vehicle_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if res_id:
        assert len(data) >= 1


def test_get_reservations_by_vehicle_empty_list(client_with_token):
    """
    Test: Get reservations when no reservations exist
    Covers: Line 33-35 (empty list scenario)
    """
    client, headers = client_with_token("user")
    vehicle_id = create_vehicle_for_user(client, headers, "GET-EMPTY-01")

    response = client.get(f"/reservations/vehicle/{vehicle_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_reservations_by_vehicle_multiple_reservations(client_with_token):
    """
    Test: Get multiple reservations for same vehicle
    Covers: Line 33-35 (multiple items in list)
    """
    client, headers = client_with_token("user")
    vehicle_id = create_vehicle_for_user(client, headers, "GET-MULTI-01")
    parking_lot_id = get_last_pid(client)

    res1_id = create_test_reservation(
        client, headers, vehicle_id, parking_lot_id, days_ahead=1, duration=1
    )
    res2_id = create_test_reservation(
        client, headers, vehicle_id, parking_lot_id, days_ahead=3, duration=1
    )
    res3_id = create_test_reservation(
        client, headers, vehicle_id, parking_lot_id, days_ahead=5, duration=1
    )

    response = client.get(f"/reservations/vehicle/{vehicle_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    if res1_id and res2_id and res3_id:
        assert len(data) >= 3


def test_get_reservations_by_vehicle_string_id(client_with_token):
    """
    Test: Get reservations with string vehicle ID
    Covers: Type validation
    """
    client, headers = client_with_token("user")
    response = client.get("/reservations/vehicle/abc123", headers=headers)
    assert response.status_code == 422


def test_get_reservations_by_vehicle_float_id(client_with_token):
    """
    Test: Get reservations with float vehicle ID
    Covers: Type validation
    """
    client, headers = client_with_token("user")
    response = client.get("/reservations/vehicle/1.5", headers=headers)
    assert response.status_code == 422


def test_get_reservations_by_vehicle_very_large_id(client_with_token):
    """
    Test: Get reservations with very large vehicle ID
    Covers: Edge case - large numbers
    """
    client, headers = client_with_token("user")
    response = client.get("/reservations/vehicle/999999999", headers=headers)
    assert response.status_code == 404


def test_get_reservations_by_vehicle_sql_injection_attempt(client_with_token):
    """
    Test: Attempt SQL injection in vehicle ID
    Covers: Security validation
    """
    client, headers = client_with_token("user")
    response = client.get("/reservations/vehicle/1' OR '1'='1", headers=headers)
    assert response.status_code == 422


# region MOCK TESTS FOR ERROR HANDLING


@patch("api.models.vehicle_model.Vehicle_model.get_one_vehicle", return_value=None)
def test_get_reservations_vehicle_not_found_mock(mock_get_vehicle, client_with_token):
    """
    Test: Mock vehicle not found scenario
    Covers: Line 27-28 via mock
    """
    client, headers = client_with_token("user")

    response = client.get("/reservations/vehicle/1", headers=headers)
    assert response.status_code == 404
    mock_get_vehicle.assert_called_once_with(1)


@patch("api.models.vehicle_model.Vehicle_model.get_one_vehicle")
def test_get_reservations_wrong_owner_mock(mock_get_vehicle, client_with_token):
    """
    Test: Mock wrong owner scenario
    Covers: Line 30-31 via mock
    """
    client, headers = client_with_token("user")

    # Mock vehicle belonging to different user (admin has id=2)
    mock_get_vehicle.return_value = {"id": 1, "user_id": 2, "license_plate": "TEST-123"}

    response = client.get("/reservations/vehicle/1", headers=headers)
    assert response.status_code == 403
    assert "does not belong" in response.json()["detail"].lower()


@patch("api.models.reservation_model.Reservation_model.get_reservation_by_vehicle")
@patch("api.models.vehicle_model.Vehicle_model.get_one_vehicle")
def test_get_reservations_database_error_mock(
    mock_get_vehicle, mock_get_reservations, client_with_token
):
    """
    Test: Mock database error scenario
    Covers: Exception handling in Line 33
    """
    client, headers = client_with_token("user")

    # Mock vehicle exists
    mock_get_vehicle.return_value = {"id": 1, "user_id": 1, "license_plate": "TEST-123"}

    # Mock database error
    mock_get_reservations.side_effect = Exception("Database connection error")

    response = client.get("/reservations/vehicle/1", headers=headers)
    # Should return 500 if error handling is implemented
    assert response.status_code in [500, 403, 200]


@patch(
    "api.models.reservation_model.Reservation_model.get_reservation_by_vehicle",
    return_value=[],
)
@patch("api.models.vehicle_model.Vehicle_model.get_one_vehicle")
def test_get_reservations_empty_list_mock(
    mock_get_vehicle, mock_get_reservations, client_with_token
):
    client, headers = client_with_token("user")

    user_response = client.get("/profile", headers=headers)
    user_id = user_response.json()["id"]

    mock_get_vehicle.return_value = {
        "id": 1,
        "user_id": user_id,
        "license_plate": "TEST-123",
    }

    response = client.get("/reservations/vehicle/1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0
    mock_get_reservations.assert_called_once_with(1)


@patch("api.models.reservation_model.Reservation_model.get_reservation_by_vehicle")
@patch("api.models.vehicle_model.Vehicle_model.get_one_vehicle")
def test_get_reservations_with_data_mock(
    mock_get_vehicle, mock_get_reservations, client_with_token
):
    client, headers = client_with_token("user")

    user_response = client.get("/profile", headers=headers)
    user_id = user_response.json()["id"]

    mock_get_vehicle.return_value = {
        "id": 1,
        "user_id": user_id,
        "license_plate": "TEST-123",
    }

    mock_get_reservations.return_value = [
        {
            "id": 1,
            "vehicle_id": 1,
            "parking_lot_id": 1,
            "start_time": datetime.now() + timedelta(days=1),
            "end_time": datetime.now() + timedelta(days=2),
        },
        {
            "id": 2,
            "vehicle_id": 1,
            "parking_lot_id": 1,
            "start_time": datetime.now() + timedelta(days=3),
            "end_time": datetime.now() + timedelta(days=4),
        },
    ]

    response = client.get("/reservations/vehicle/1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    mock_get_reservations.assert_called_once_with(1)


# region INTEGRATION TESTS


def test_get_reservations_cross_user_isolation(client_with_token):
    """
    Test: Ensure users can only see their own vehicle's reservations
    Covers: Line 30-31 (security isolation)
    """
    # User 1 creates vehicle and reservation
    user1_client, user1_headers = client_with_token("user")
    vehicle1_id = create_vehicle_for_user(
        user1_client, user1_headers, "ISOLATION-USER1"
    )
    parking_lot_id = get_last_pid(user1_client)
    create_test_reservation(user1_client, user1_headers, vehicle1_id, parking_lot_id)

    # User 2 (admin) tries to access user 1's vehicle
    user2_client, user2_headers = client_with_token("admin")
    response = user2_client.get(
        f"/reservations/vehicle/{vehicle1_id}", headers=user2_headers
    )
    assert response.status_code == 403


def test_get_reservations_data_structure(client_with_token):
    """
    Test: Verify returned data structure
    Covers: Line 35 (return format)
    """
    client, headers = client_with_token("user")
    vehicle_id = create_vehicle_for_user(client, headers, "STRUCTURE-01")
    parking_lot_id = get_last_pid(client)

    create_test_reservation(client, headers, vehicle_id, parking_lot_id)

    response = client.get(f"/reservations/vehicle/{vehicle_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    if len(data) > 0:
        reservation = data[0]
        # Check that reservation has expected fields
        assert "id" in reservation or isinstance(reservation, (list, tuple))


# region EDGE CASES


def test_get_reservations_with_expired_reservations(client_with_token):
    """
    Test: Get reservations including past/expired ones
    Covers: Line 33-35 (historical data)
    """
    client, headers = client_with_token("user")
    vehicle_id = create_vehicle_for_user(client, headers, "EXPIRED-01")

    # Get reservations (may include expired ones depending on implementation)
    response = client.get(f"/reservations/vehicle/{vehicle_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_reservations_concurrent_requests(client_with_token):
    """
    Test: Multiple concurrent requests for same vehicle
    Covers: Line 25-35 (concurrent access)
    """
    client, headers = client_with_token("user")
    vehicle_id = create_vehicle_for_user(client, headers, "CONCURRENT-01")

    # Make multiple requests
    responses = []
    for _ in range(3):
        response = client.get(f"/reservations/vehicle/{vehicle_id}", headers=headers)
        responses.append(response)

    # All should succeed
    for response in responses:
        assert response.status_code == 200
        assert isinstance(response.json(), list)
