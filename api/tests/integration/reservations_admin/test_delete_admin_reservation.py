# import pytest
# from datetime import datetime, timedelta
# from api.tests.conftest import get_last_vid, get_last_pid


# # region DELETE /admin/reservations/{reservation_id}
# def test_admin_delete_reservation_success(client_with_token):
#     """Test successfully deleting a reservation as admin"""
#     client, headers = client_with_token("admin")
#     vehicle_id = get_last_vid(client_with_token)
#     parking_lot_id = get_last_pid(client)

#     # Create a reservation first
#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": parking_lot_id,
#         "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
#         "end_time": (datetime.now() + timedelta(hours=3)).isoformat(),
#     }
#     create_response = client.post(
#         "/admin/reservations", json=reservation_data, headers=headers
#     )
#     reservation_id = create_response.json()["reservation_id"]

#     # Delete the reservation
#     response = client.delete(f"/admin/reservations/{reservation_id}", headers=headers)

#     assert response.status_code == 200
#     assert "message" in response.json()
#     assert response.json()["message"] == "Reservation deleted"


# def test_admin_delete_reservation_as_superadmin(client_with_token):
#     """Test successfully deleting a reservation as superadmin"""
#     client, headers = client_with_token("superadmin")
#     vehicle_id = get_last_vid(client_with_token)
#     parking_lot_id = get_last_pid(client)

#     # Create a reservation first
#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": parking_lot_id,
#         "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
#         "end_time": (datetime.now() + timedelta(hours=3)).isoformat(),
#     }
#     create_response = client.post(
#         "/admin/reservations", json=reservation_data, headers=headers
#     )
#     reservation_id = create_response.json()["reservation_id"]

#     # Delete the reservation
#     response = client.delete(f"/admin/reservations/{reservation_id}", headers=headers)

#     assert response.status_code == 200
#     assert "message" in response.json()
#     assert response.json()["message"] == "Reservation deleted"


# def test_admin_delete_reservation_not_found(client_with_token):
#     """Test deleting a non-existent reservation"""
#     client, headers = client_with_token("admin")

#     response = client.delete("/admin/reservations/99999", headers=headers)

#     assert response.status_code == 404
#     assert "Reservation not found" in response.json()["detail"]


# def test_admin_delete_reservation_as_user_forbidden(client_with_token):
#     """Test that regular users cannot delete admin reservations"""
#     admin_client, admin_headers = client_with_token("admin")
#     vehicle_id = get_last_vid(client_with_token)
#     parking_lot_id = get_last_pid(admin_client)

#     # Create a reservation as admin
#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": parking_lot_id,
#         "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
#         "end_time": (datetime.now() + timedelta(hours=3)).isoformat(),
#     }
#     create_response = admin_client.post(
#         "/admin/reservations", json=reservation_data, headers=admin_headers
#     )
#     reservation_id = create_response.json()["reservation_id"]

#     # Try to delete as regular user
#     user_client, user_headers = client_with_token("user")
#     response = user_client.delete(
#         f"/admin/reservations/{reservation_id}", headers=user_headers
#     )

#     assert response.status_code == 403


# def test_admin_delete_reservation_no_authentication(client):
#     """Test deleting admin reservation without authentication"""
#     response = client.delete("/admin/reservations/1")

#     assert response.status_code == 401


# def test_admin_delete_reservation_invalid_id(client_with_token):
#     """Test deleting reservation with invalid ID format"""
#     client, headers = client_with_token("admin")

#     response = client.delete("/admin/reservations/invalid", headers=headers)

#     assert response.status_code == 422


# def test_admin_delete_reservation_negative_id(client_with_token):
#     """Test deleting reservation with negative ID"""
#     client, headers = client_with_token("admin")

#     response = client.delete("/admin/reservations/-1", headers=headers)

#     assert response.status_code == 404


# def test_admin_delete_reservation_zero_id(client_with_token):
#     """Test deleting reservation with ID of 0"""
#     client, headers = client_with_token("admin")

#     response = client.delete("/admin/reservations/0", headers=headers)

#     assert response.status_code == 404


# # endregion
