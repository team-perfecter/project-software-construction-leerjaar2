import pytest
from datetime import datetime, timedelta
from api.tests.conftest import get_last_vid, get_last_pid


# region DELETE /reservations/delete/{reservation_id}
def test_delete_reservation_success(client_with_token):
    """Test successfully deleting a reservation"""
    client, headers = client_with_token("superadmin")  # Changed from "user" to "superadmin"
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    # Create a reservation first
    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),  # Changed to start_time
        "end_time": (datetime.now() + timedelta(hours=3)).isoformat(),    # Changed to end_time
    }
    create_response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert create_response.status_code == 200  # Verify reservation was created

    # Get the created reservation ID
    get_response = client.get(f"/reservations/vehicle/{vehicle_id}", headers=headers)
    assert get_response.status_code == 200
    reservations = get_response.json()
    assert len(reservations) > 0, "No reservations found after creation"
    reservation_id = reservations[-1]["id"]

    # Delete the reservation
    response = client.delete(f"/reservations/delete/{reservation_id}", headers=headers)

    assert response.status_code == 200
    assert "Reservation deleted successfully" in response.json()["detail"]["message"]


def test_delete_reservation_not_found(client_with_token):
    """Test deleting a non-existent reservation"""
    client, headers = client_with_token("superadmin")  # Changed from "user" to "superadmin"

    response = client.delete("/reservations/delete/99999", headers=headers)

    assert response.status_code == 404
    assert "Reservation not found" in response.json()["detail"]["message"]


def test_delete_reservation_not_owned(client_with_token):
    """Test deleting a reservation that belongs to another user"""
    # Create reservation as superadmin (who owns the vehicle)
    superadmin_client, superadmin_headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(superadmin_client)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),  # Changed to start_time
        "end_time": (datetime.now() + timedelta(hours=3)).isoformat(),    # Changed to end_time
    }
    create_response = superadmin_client.post(
        "/reservations/create", json=reservation_data, headers=superadmin_headers
    )
    assert create_response.status_code == 200  # Verify reservation was created

    # Get reservation ID
    get_response = superadmin_client.get(
        f"/reservations/vehicle/{vehicle_id}", headers=superadmin_headers
    )
    assert get_response.status_code == 200
    reservations = get_response.json()
    assert len(reservations) > 0, "No reservations found after creation"
    reservation_id = reservations[-1]["id"]

    # Try to delete as different user
    user_client, user_headers = client_with_token("extrauser")
    response = user_client.delete(
        f"/reservations/delete/{reservation_id}", headers=user_headers
    )

    assert response.status_code == 403
    assert (
        "This reservation does not belong to the logged-in user"
        in response.json()["detail"]["message"]
    )


def test_delete_reservation_no_authentication(client):
    """Test deleting reservation without authentication"""
    response = client.delete("/reservations/delete/1")

    assert response.status_code == 401


def test_delete_reservation_invalid_id(client_with_token):
    """Test deleting reservation with invalid ID format"""
    client, headers = client_with_token("superadmin")  # Changed from "user" to "superadmin"

    response = client.delete("/reservations/delete/invalid", headers=headers)

    assert response.status_code == 422


def test_delete_reservation_negative_id(client_with_token):
    """Test deleting reservation with negative ID"""
    client, headers = client_with_token("superadmin")  # Changed from "user" to "superadmin"

    response = client.delete("/reservations/delete/-1", headers=headers)

    assert response.status_code == 404


def test_delete_reservation_zero_id(client_with_token):
    """Test deleting reservation with ID of 0"""
    client, headers = client_with_token("superadmin")  # Changed from "user" to "superadmin"

    response = client.delete("/reservations/delete/0", headers=headers)

    assert response.status_code == 404


# endregion
