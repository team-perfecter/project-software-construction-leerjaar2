# import pytest
# from datetime import datetime, timedelta
# from api.tests.conftest import get_last_vid, get_last_pid


# # region POST /admin/reservations
# def test_admin_create_reservation_success(client_with_token):
#     """Test successfully creating a reservation as admin"""
#     client, headers = client_with_token("admin")
#     vehicle_id = get_last_vid(client_with_token)
#     parking_lot_id = get_last_pid(client)

#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": parking_lot_id,
#         "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
#         "end_time": (datetime.now() + timedelta(hours=3)).isoformat(),
#     }

#     response = client.post(
#         "/admin/reservations", json=reservation_data, headers=headers
#     )

#     assert response.status_code == 201
#     assert "message" in response.json()
#     assert response.json()["message"] == "Reservation created"
#     assert "reservation_id" in response.json()


# def test_admin_create_reservation_as_superadmin(client_with_token):
#     """Test successfully creating a reservation as superadmin"""
#     client, headers = client_with_token("superadmin")
#     vehicle_id = get_last_vid(client_with_token)
#     parking_lot_id = get_last_pid(client)

#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": parking_lot_id,
#         "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
#         "end_time": (datetime.now() + timedelta(hours=3)).isoformat(),
#     }

#     response = client.post(
#         "/admin/reservations", json=reservation_data, headers=headers
#     )

#     assert response.status_code == 201
#     assert "message" in response.json()
#     assert response.json()["message"] == "Reservation created"


# def test_admin_create_reservation_parking_lot_not_found(client_with_token):
#     """Test creating reservation with non-existent parking lot"""
#     client, headers = client_with_token("admin")
#     vehicle_id = get_last_vid(client_with_token)

#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": 99999,
#         "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
#         "end_time": (datetime.now() + timedelta(hours=3)).isoformat(),
#     }

#     response = client.post(
#         "/admin/reservations", json=reservation_data, headers=headers
#     )

#     assert response.status_code == 404
#     assert "Parking lot not found" in response.json()["detail"]


# def test_admin_create_reservation_vehicle_not_found(client_with_token):
#     """Test creating reservation with non-existent vehicle"""
#     client, headers = client_with_token("admin")
#     parking_lot_id = get_last_pid(client)

#     reservation_data = {
#         "vehicle_id": 99999,
#         "parking_lot_id": parking_lot_id,
#         "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
#         "end_time": (datetime.now() + timedelta(hours=3)).isoformat(),
#     }

#     response = client.post(
#         "/admin/reservations", json=reservation_data, headers=headers
#     )

#     assert response.status_code == 404
#     assert "Vehicle not found" in response.json()["detail"]


# def test_admin_create_reservation_as_user_forbidden(client_with_token):
#     """Test that regular users cannot create admin reservations"""
#     client, headers = client_with_token("user")
#     vehicle_id = get_last_vid(client_with_token)
#     parking_lot_id = get_last_pid(client)

#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": parking_lot_id,
#         "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
#         "end_time": (datetime.now() + timedelta(hours=3)).isoformat(),
#     }

#     response = client.post(
#         "/admin/reservations", json=reservation_data, headers=headers
#     )

#     assert response.status_code == 403


# def test_admin_create_reservation_no_authentication(client):
#     """Test creating admin reservation without authentication"""
#     reservation_data = {
#         "vehicle_id": 1,
#         "parking_lot_id": 1,
#         "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
#         "end_time": (datetime.now() + timedelta(hours=3)).isoformat(),
#     }

#     response = client.post("/admin/reservations", json=reservation_data)

#     assert response.status_code == 401


# def test_admin_create_reservation_missing_fields(client_with_token):
#     """Test creating admin reservation with missing required fields"""
#     client, headers = client_with_token("admin")

#     reservation_data = {
#         "vehicle_id": 1,
#         "parking_lot_id": 1,
#         # Missing start_time and end_time
#     }

#     response = client.post(
#         "/admin/reservations", json=reservation_data, headers=headers
#     )

#     assert response.status_code == 422


# def test_admin_create_reservation_invalid_date_format(client_with_token):
#     """Test creating admin reservation with invalid date format"""
#     client, headers = client_with_token("admin")
#     vehicle_id = get_last_vid(client_with_token)
#     parking_lot_id = get_last_pid(client)

#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": parking_lot_id,
#         "start_time": "invalid-date",
#         "end_time": "invalid-date",
#     }

#     response = client.post(
#         "/admin/reservations", json=reservation_data, headers=headers
#     )

#     assert response.status_code == 422


# # endregion
