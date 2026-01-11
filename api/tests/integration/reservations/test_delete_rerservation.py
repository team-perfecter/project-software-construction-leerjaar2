import pytest
from datetime import datetime, timedelta
from api.tests.conftest import get_last_vid, get_last_pid


# region DELETE /reservations/delete/{reservation_id}
def test_delete_reservation_success(client_with_token):
    """Test successfully deleting a reservation"""
    client, headers = client_with_token("user")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    # Create a reservation first
    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_date": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_date": (datetime.now() + timedelta(hours=3)).isoformat(),
    }
    create_response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    # Get the created reservation ID
    # Since the response doesn't include the ID, we'll get it from the reservations list
    get_response = client.get(f"/reservations/vehicle/{vehicle_id}", headers=headers)
    reservations = get_response.json()
    reservation_id = reservations[-1]["id"]

    # Delete the reservation
    response = client.delete(f"/reservations/delete/{reservation_id}", headers=headers)

    assert response.status_code == 200
    assert "Reservation deleted successfully" in response.json()["detail"]["message"]


def test_delete_reservation_not_found(client_with_token):
    """Test deleting a non-existent reservation"""
    client, headers = client_with_token("user")

    response = client.delete("/reservations/delete/99999", headers=headers)

    assert response.status_code == 404
    assert "Reservation not found" in response.json()["detail"]["message"]


def test_delete_reservation_not_owned(client_with_token):
    """Test deleting a reservation that belongs to another user"""
    # Create reservation as user 1
    user1_client, user1_headers = client_with_token("user")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(user1_client)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_date": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_date": (datetime.now() + timedelta(hours=3)).isoformat(),
    }
    user1_client.post(
        "/reservations/create", json=reservation_data, headers=user1_headers
    )

    # Get reservation ID
    get_response = user1_client.get(
        f"/reservations/vehicle/{vehicle_id}", headers=user1_headers
    )
    reservations = get_response.json()
    reservation_id = reservations[-1]["id"]

    # Try to delete as different user
    user2_client, user2_headers = client_with_token("extrauser")
    response = user2_client.delete(
        f"/reservations/delete/{reservation_id}", headers=user2_headers
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
    client, headers = client_with_token("user")

    response = client.delete("/reservations/delete/invalid", headers=headers)

    assert response.status_code == 422


def test_delete_reservation_negative_id(client_with_token):
    """Test deleting reservation with negative ID"""
    client, headers = client_with_token("user")

    response = client.delete("/reservations/delete/-1", headers=headers)

    assert response.status_code == 404


def test_delete_reservation_zero_id(client_with_token):
    """Test deleting reservation with ID of 0"""
    client, headers = client_with_token("user")

    response = client.delete("/reservations/delete/0", headers=headers)

    assert response.status_code == 404


# endregion
