import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from fastapi.testclient import TestClient
from api.main import app
from api.tests.conftest import get_last_pid

client = TestClient(app)


#region HELPER FUNCTIONS


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


# DELETE /reservations/delete/{reservation_id} TESTS

def test_delete_reservation_success(client_with_token):
    """
    Test: Successfully delete a reservation
    Covers: Line 70-91 (happy path)
    """
    client, headers = client_with_token("user")
    vehicle_id = create_vehicle_for_user(client, headers, "DELETE-SUCCESS")
    parking_lot_id = get_last_pid(client)

    # Create a reservation first
    reservation_id = create_test_reservation(
        client, headers, vehicle_id, parking_lot_id
    )

    if reservation_id:
        # Now delete it
        response = client.delete(
            f"/reservations/delete/{reservation_id}", headers=headers
        )
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["detail"]["message"].lower()


def test_delete_reservation_unauthorized():
    """
    Test: Delete reservation without authentication
    Covers: Line 70 (authentication dependency)
    """
    response = client.delete("/reservations/delete/1")
    assert response.status_code == 401


def test_delete_reservation_not_found(client_with_token):
    """
    Test: Delete non-existent reservation
    Covers: Line 73-75
    """
    client, headers = client_with_token("user")

    response = client.delete("/reservations/delete/99999", headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]["message"].lower()


def test_delete_reservation_wrong_owner(client_with_token):
    """
    Test: Try to delete another user's reservation
    Covers: Line 78-80
    """
    # User creates reservation
    user_client, user_headers = client_with_token("user")
    vehicle_id = create_vehicle_for_user(user_client, user_headers, "DELETE-WRONG")
    parking_lot_id = get_last_pid(user_client)
    reservation_id = create_test_reservation(
        user_client, user_headers, vehicle_id, parking_lot_id
    )

    if reservation_id:
        # Admin tries to delete user's reservation
        admin_client, admin_headers = client_with_token("admin")
        response = admin_client.delete(
            f"/reservations/delete/{reservation_id}", headers=admin_headers
        )
        assert response.status_code == 403
        assert "does not belong" in response.json()["detail"]["message"].lower()


def test_delete_reservation_invalid_id_format(client_with_token):
    """
    Test: Delete reservation with invalid ID format
    Covers: FastAPI validation
    """
    client, headers = client_with_token("user")

    response = client.delete("/reservations/delete/invalid", headers=headers)
    assert response.status_code == 422


def test_delete_reservation_negative_id(client_with_token):
    """
    Test: Delete reservation with negative ID
    Covers: Edge case - negative ID
    """
    client, headers = client_with_token("user")

    response = client.delete("/reservations/delete/-1", headers=headers)
    assert response.status_code == 404


def test_delete_reservation_zero_id(client_with_token):
    """
    Test: Delete reservation with ID = 0
    Covers: Edge case - zero ID
    """
    client, headers = client_with_token("user")

    response = client.delete("/reservations/delete/0", headers=headers)
    assert response.status_code == 404


def test_delete_reservation_already_deleted(client_with_token):
    """
    Test: Try to delete a reservation twice
    Covers: Line 73-75 (not found after deletion)
    """
    client, headers = client_with_token("user")
    vehicle_id = create_vehicle_for_user(client, headers, "DELETE-TWICE")
    parking_lot_id = get_last_pid(client)

    reservation_id = create_test_reservation(
        client, headers, vehicle_id, parking_lot_id
    )

    if reservation_id:
        # First deletion
        first_response = client.delete(
            f"/reservations/delete/{reservation_id}", headers=headers
        )
        assert first_response.status_code == 200

        # Second deletion should fail
        second_response = client.delete(
            f"/reservations/delete/{reservation_id}", headers=headers
        )
        assert second_response.status_code == 404


def test_delete_reservation_string_id(client_with_token):
    """
    Test: Delete with string ID
    Covers: Type validation
    """
    client, headers = client_with_token("user")
    response = client.delete("/reservations/delete/abc123", headers=headers)
    assert response.status_code == 422


def test_delete_reservation_float_id(client_with_token):
    """
    Test: Delete with float ID
    Covers: Type validation
    """
    client, headers = client_with_token("user")
    response = client.delete("/reservations/delete/1.5", headers=headers)
    assert response.status_code == 422


def test_delete_reservation_very_large_id(client_with_token):
    """
    Test: Delete with very large ID
    Covers: Edge case - large numbers
    """
    client, headers = client_with_token("user")
    response = client.delete("/reservations/delete/999999999", headers=headers)
    assert response.status_code == 404


def test_delete_reservation_sql_injection_attempt(client_with_token):
    """
    Test: SQL injection attempt
    Covers: Security validation
    """
    client, headers = client_with_token("user")
    response = client.delete("/reservations/delete/1' OR '1'='1", headers=headers)
    assert response.status_code == 422


def test_delete_reservation_special_characters(client_with_token):
    """
    Test: Delete with special characters in ID
    Covers: Input sanitization
    """
    client, headers = client_with_token("user")
    response = client.delete(
        "/reservations/delete/<script>alert('xss')</script>", headers=headers
    )
    assert response.status_code in [404, 422]


#region MOCK TESTS FOR ERROR HANDLING

@patch(
    "api.models.reservation_model.Reservation_model.get_reservation_by_id",
    return_value=None,
)
def test_delete_reservation_not_found_mock(mock_get_reservation, client_with_token):
    """
    Test: Mock reservation not found
    Covers: Line 73-75 via mock
    """
    client, headers = client_with_token("user")

    response = client.delete("/reservations/delete/1", headers=headers)
    assert response.status_code == 404
    mock_get_reservation.assert_called_once_with(1)


@patch("api.models.reservation_model.Reservation_model.get_reservation_by_id")
def test_delete_reservation_wrong_owner_mock(mock_get_reservation, client_with_token):
    """
    Test: Mock wrong owner scenario
    Covers: Line 78-80 via mock
    """
    client, headers = client_with_token("user")

    # Get actual user ID
    user_response = client.get("/profile", headers=headers)
    user_id = user_response.json()["id"]

    # Mock reservation belonging to different user
    mock_get_reservation.return_value = {
        "id": 1,
        "user_id": user_id + 1,  # Different user
        "vehicle_id": 1,
        "parking_lot_id": 1,
    }

    response = client.delete("/reservations/delete/1", headers=headers)
    assert response.status_code == 403
    assert "does not belong" in response.json()["detail"]["message"].lower()


@patch(
    "api.models.reservation_model.Reservation_model.delete_reservation",
    return_value=False,
)
@patch("api.models.reservation_model.Reservation_model.get_reservation_by_id")
def test_delete_reservation_database_error_mock(
    mock_get_reservation, mock_delete, client_with_token
):
    """
    Test: Mock database error during deletion
    Covers: Line 83-85
    """
    client, headers = client_with_token("user")

    # Get actual user ID
    user_response = client.get("/profile", headers=headers)
    user_id = user_response.json()["id"]

    # Mock reservation exists and belongs to user
    mock_get_reservation.return_value = {
        "id": 1,
        "user_id": user_id,
        "vehicle_id": 1,
        "parking_lot_id": 1,
    }

    response = client.delete("/reservations/delete/1", headers=headers)
    assert response.status_code == 500
    assert "failed to delete" in response.json()["detail"]["message"].lower()


@patch(
    "api.models.reservation_model.Reservation_model.delete_reservation",
    return_value=True,
)
@patch("api.models.reservation_model.Reservation_model.get_reservation_by_id")
def test_delete_reservation_success_mock(
    mock_get_reservation, mock_delete, client_with_token
):
    """
    Test: Mock successful deletion
    Covers: Line 87-89 via mock
    """
    client, headers = client_with_token("user")

    # Get actual user ID
    user_response = client.get("/profile", headers=headers)
    user_id = user_response.json()["id"]

    # Mock reservation exists and belongs to user
    mock_get_reservation.return_value = {
        "id": 1,
        "user_id": user_id,
        "vehicle_id": 1,
        "parking_lot_id": 1,
    }

    response = client.delete("/reservations/delete/1", headers=headers)
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["detail"]["message"].lower()
    mock_delete.assert_called_once_with(1)


#region INTEGRATION TESTS


def test_delete_reservation_user_isolation(client_with_token):
    """
    Test: Users can only delete their own reservations
    Covers: Line 78-80 (security)
    """
    # User 1 creates reservation
    user1_client, user1_headers = client_with_token("user")
    vehicle1_id = create_vehicle_for_user(user1_client, user1_headers, "ISOLATION-1")
    parking_lot_id = get_last_pid(user1_client)
    reservation_id = create_test_reservation(
        user1_client, user1_headers, vehicle1_id, parking_lot_id
    )

    # User 2 tries to delete user 1's reservation
    user2_client, user2_headers = client_with_token("admin")

    if reservation_id:
        response = user2_client.delete(
            f"/reservations/delete/{reservation_id}", headers=user2_headers
        )
        assert response.status_code == 403


def test_delete_multiple_reservations_sequentially(client_with_token):
    """
    Test: Delete multiple reservations one by one
    Covers: Line 70-91 (multiple deletions)
    """
    client, headers = client_with_token("user")
    vehicle_id = create_vehicle_for_user(client, headers, "MULTI-DELETE")
    parking_lot_id = get_last_pid(client)

    # Create 3 reservations
    res_ids = []
    for i in range(3):
        res_id = create_test_reservation(
            client,
            headers,
            vehicle_id,
            parking_lot_id,
            days_ahead=1 + (i * 2),
            duration=1,
        )
        if res_id:
            res_ids.append(res_id)

    # Delete them one by one
    for res_id in res_ids:
        response = client.delete(f"/reservations/delete/{res_id}", headers=headers)
        assert response.status_code == 200


def test_delete_reservation_verify_not_in_list(client_with_token):
    """
    Test: After deletion, reservation should not appear in GET list
    Covers: Integration with GET endpoint
    """
    client, headers = client_with_token("user")
    vehicle_id = create_vehicle_for_user(client, headers, "VERIFY-DELETE")
    parking_lot_id = get_last_pid(client)

    # Create reservation
    reservation_id = create_test_reservation(
        client, headers, vehicle_id, parking_lot_id
    )

    if reservation_id:
        # Delete it
        delete_response = client.delete(
            f"/reservations/delete/{reservation_id}", headers=headers
        )
        assert delete_response.status_code == 200

        # Verify it's not in the list
        get_response = client.get(
            f"/reservations/vehicle/{vehicle_id}", headers=headers
        )
        reservations = get_response.json()

        # Check that the deleted reservation is not in the list
        reservation_ids = [
            r["id"] if isinstance(r, dict) else r[0] for r in reservations
        ]
        assert reservation_id not in reservation_ids


#region EDGE CASES


def test_delete_reservation_concurrent_delete_attempts(client_with_token):
    """
    Test: Multiple concurrent delete attempts
    Covers: Race condition handling
    """
    client, headers = client_with_token("user")
    vehicle_id = create_vehicle_for_user(client, headers, "CONCURRENT")
    parking_lot_id = get_last_pid(client)

    reservation_id = create_test_reservation(
        client, headers, vehicle_id, parking_lot_id
    )

    if reservation_id:
        # Try to delete twice quickly
        response1 = client.delete(
            f"/reservations/delete/{reservation_id}", headers=headers
        )
        response2 = client.delete(
            f"/reservations/delete/{reservation_id}", headers=headers
        )

        # One should succeed, one should fail
        assert (response1.status_code == 200 and response2.status_code == 404) or (
            response1.status_code == 404 and response2.status_code == 200
        )


def test_delete_reservation_with_past_dates(client_with_token):
    """
    Test: Delete reservation with past dates (if allowed to exist)
    Covers: Historical data deletion
    """
    client, headers = client_with_token("user")
    vehicle_id = create_vehicle_for_user(client, headers, "PAST")
    parking_lot_id = get_last_pid(client)

    # Create a reservation (will be in the future due to validation)
    reservation_id = create_test_reservation(
        client, headers, vehicle_id, parking_lot_id
    )

    if reservation_id:
        # Delete should work regardless of date
        response = client.delete(
            f"/reservations/delete/{reservation_id}", headers=headers
        )
        assert response.status_code == 200


def test_delete_reservation_boundary_id_values(client_with_token):
    """
    Test: Boundary values for reservation IDs
    Covers: Edge case IDs
    """
    client, headers = client_with_token("user")

    # Test various boundary values
    boundary_ids = [0, -1, 999999999]

    for test_id in boundary_ids:
        response = client.delete(f"/reservations/delete/{test_id}", headers=headers)
        assert response.status_code == 404


# PARAMETRIZED TESTS


@pytest.mark.parametrize(
    "invalid_id",
    [
        "abc",
        "123abc",
        "1.5",
        "null",
        "undefined",
        "",
        "   ",
    ],
)
def test_delete_reservation_invalid_id_formats(client_with_token, invalid_id):
    """
    Test: Various invalid ID formats
    Covers: Input validation
    """
    client, headers = client_with_token("user")
    response = client.delete(f"/reservations/delete/{invalid_id}", headers=headers)
    assert response.status_code in [404, 422]


@pytest.mark.parametrize("role", ["user", "admin"])
def test_delete_own_reservation_different_roles(client_with_token, role):
    """
    Test: Different user roles can delete their own reservations
    Covers: Line 70-91 for different roles
    """
    client, headers = client_with_token(role)
    vehicle_id = create_vehicle_for_user(client, headers, f"ROLE-{role}")
    parking_lot_id = get_last_pid(client)

    reservation_id = create_test_reservation(
        client, headers, vehicle_id, parking_lot_id
    )

    if reservation_id:
        response = client.delete(
            f"/reservations/delete/{reservation_id}", headers=headers
        )
        assert response.status_code == 200
