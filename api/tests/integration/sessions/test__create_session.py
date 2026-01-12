# import pytest
# from datetime import datetime, timedelta
# from api.tests.conftest import get_last_vid


# # region POST /parking-lots/{lid}/sessions/start
# def test_start_session_success(client_with_token):
#     """Test successfully starting a parking session"""
#     client, headers = client_with_token("user")
#     vehicle_id = get_last_vid(client_with_token)

#     response = client.post(
#         "/parking-lots/1/sessions/start",
#         params={"vehicle_id": vehicle_id},
#         headers=headers,
#     )

#     assert response.status_code == 201
#     data = response.json()
#     assert data["message"] == "Session started successfully"
#     assert data["parking_lot_id"] == 1
#     assert data["vehicle_id"] == vehicle_id


# def test_start_session_parking_lot_not_found(client_with_token):
#     """Test starting session with non-existent parking lot"""
#     client, headers = client_with_token("user")
#     vehicle_id = get_last_vid(client_with_token)

#     response = client.post(
#         "/parking-lots/99999/sessions/start",
#         params={"vehicle_id": vehicle_id},
#         headers=headers,
#     )

#     assert response.status_code == 404
#     assert "Parking lot not found" in response.json()["detail"]["error"]


# def test_start_session_vehicle_not_found(client_with_token):
#     """Test starting session with non-existent vehicle"""
#     client, headers = client_with_token("user")

#     response = client.post(
#         "/parking-lots/1/sessions/start", params={"vehicle_id": 99999}, headers=headers
#     )

#     assert response.status_code == 404
#     assert "Vehicle not found" in response.json()["detail"]["error"]


# def test_start_session_vehicle_not_owned(client_with_token):
#     """Test starting session with vehicle not owned by user"""
#     # Create vehicle as superadmin
#     superadmin_client, superadmin_headers = client_with_token("superadmin")
#     vehicle = {
#         "user_id": 1,
#         "license_plate": "XYZ789",
#         "make": "Ford",
#         "model": "Focus",
#         "color": "Red",
#         "year": 2021,
#     }
#     create_response = superadmin_client.post(
#         "/vehicles/create", json=vehicle, headers=superadmin_headers
#     )
#     vehicle_id = create_response.json()["vehicle"]["id"]

#     # Try to start session as different user
#     user_client, user_headers = client_with_token("extrauser")
#     response = user_client.post(
#         "/parking-lots/1/sessions/start",
#         params={"vehicle_id": vehicle_id},
#         headers=user_headers,
#     )

#     assert response.status_code == 403
#     assert (
#         "Vehicle does not belong to current user"
#         in response.json()["detail"]["message"]
#     )


# def test_start_session_already_active(client_with_token):
#     """Test starting session when vehicle already has active session"""
#     client, headers = client_with_token("user")
#     vehicle_id = get_last_vid(client_with_token)

#     # Start first session
#     client.post(
#         "/parking-lots/1/sessions/start",
#         params={"vehicle_id": vehicle_id},
#         headers=headers,
#     )

#     # Try to start second session
#     response = client.post(
#         "/parking-lots/1/sessions/start",
#         params={"vehicle_id": vehicle_id},
#         headers=headers,
#     )

#     assert response.status_code == 209
#     assert "This vehicle already has a session" in response.json()["message"]


# def test_start_session_no_authentication(client):
#     """Test starting session without authentication"""
#     response = client.post("/parking-lots/1/sessions/start", params={"vehicle_id": 1})

#     assert response.status_code == 401


# # endregion


# # region POST /parking-lots/{lid}/sessions/stop
# def test_stop_session_success(client_with_token):
#     """Test successfully stopping a parking session"""
#     client, headers = client_with_token("user")
#     vehicle_id = get_last_vid(client_with_token)

#     # Start session first
#     client.post(
#         "/parking-lots/1/sessions/start",
#         params={"vehicle_id": vehicle_id},
#         headers=headers,
#     )

#     # Stop session
#     response = client.post(
#         "/parking-lots/1/sessions/stop",
#         params={"vehicle_id": vehicle_id},
#         headers=headers,
#     )

#     assert response.status_code == 201
#     assert "Session stopped successfully" in response.json()["message"]


# def test_stop_session_no_active_session(client_with_token):
#     """Test stopping session when no active session exists"""
#     client, headers = client_with_token("user")
#     vehicle_id = get_last_vid(client_with_token)

#     response = client.post(
#         "/parking-lots/1/sessions/stop",
#         params={"vehicle_id": vehicle_id},
#         headers=headers,
#     )

#     assert response.status_code == 200
#     assert "This vehicle has no active sessions" in response.json()


# def test_stop_session_from_reservation_forbidden(client_with_token):
#     """Test that stopping a reservation-based session via regular endpoint is forbidden"""
#     client, headers = client_with_token("user")
#     vehicle_id = get_last_vid(client_with_token)

#     # Create a reservation
#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": 1,
#         "start_date": (datetime.now() + timedelta(hours=1)).isoformat(),
#         "end_date": (datetime.now() + timedelta(hours=3)).isoformat(),
#     }
#     reservation_response = client.post(
#         "/reservations/create", json=reservation_data, headers=headers
#     )
#     reservation_id = reservation_response.json()["reservation"]["id"]

#     # Start session from reservation
#     client.post(f"/sessions/reservations/{reservation_id}/start", headers=headers)

#     # Try to stop via regular endpoint
#     response = client.post(
#         "/parking-lots/1/sessions/stop",
#         params={"vehicle_id": vehicle_id},
#         headers=headers,
#     )

#     assert response.status_code == 403
#     assert (
#         "Cannot stop a session that was started from a reservation"
#         in response.json()["detail"]
#     )


# def test_stop_session_no_authentication(client):
#     """Test stopping session without authentication"""
#     response = client.post("/parking-lots/1/sessions/stop", params={"vehicle_id": 1})

#     assert response.status_code == 401


# # endregion


# # region POST /sessions/reservations/{reservation_id}/start
# def test_start_session_from_reservation_success(client_with_token):
#     """Test successfully starting session from reservation"""
#     client, headers = client_with_token("user")
#     vehicle_id = get_last_vid(client_with_token)

#     # Create reservation
#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": 1,
#         "start_date": (datetime.now() + timedelta(hours=1)).isoformat(),
#         "end_date": (datetime.now() + timedelta(hours=3)).isoformat(),
#     }
#     reservation_response = client.post(
#         "/reservations/create", json=reservation_data, headers=headers
#     )
#     reservation_id = reservation_response.json()["reservation"]["id"]

#     # Start session from reservation
#     response = client.post(
#         f"/sessions/reservations/{reservation_id}/start", headers=headers
#     )

#     assert response.status_code == 200
#     assert "Session started" in response.json()["message"]


# def test_start_session_from_reservation_not_found(client_with_token):
#     """Test starting session from non-existent reservation"""
#     client, headers = client_with_token("user")

#     response = client.post("/sessions/reservations/99999/start", headers=headers)

#     assert response.status_code == 404
#     assert "Reservation not found" in response.json()["detail"]


# def test_start_session_from_reservation_not_owned(client_with_token):
#     """Test starting session from reservation not owned by user"""
#     # Create reservation as one user
#     superadmin_client, superadmin_headers = client_with_token("superadmin")
#     vehicle_id = get_last_vid(client_with_token)

#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": 1,
#         "start_date": (datetime.now() + timedelta(hours=1)).isoformat(),
#         "end_date": (datetime.now() + timedelta(hours=3)).isoformat(),
#     }
#     reservation_response = superadmin_client.post(
#         "/reservations/create", json=reservation_data, headers=superadmin_headers
#     )
#     reservation_id = reservation_response.json()["reservation"]["id"]

#     # Try to start session as different user
#     user_client, user_headers = client_with_token("extrauser")
#     response = user_client.post(
#         f"/sessions/reservations/{reservation_id}/start", headers=user_headers
#     )

#     assert response.status_code == 403
#     assert "Reservation does not belong to current user" in response.json()["detail"]


# def test_start_session_from_reservation_already_exists(client_with_token):
#     """Test starting session from reservation when session already exists"""
#     client, headers = client_with_token("user")
#     vehicle_id = get_last_vid(client_with_token)

#     # Create reservation
#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": 1,
#         "start_date": (datetime.now() + timedelta(hours=1)).isoformat(),
#         "end_date": (datetime.now() + timedelta(hours=3)).isoformat(),
#     }
#     reservation_response = client.post(
#         "/reservations/create", json=reservation_data, headers=headers
#     )
#     reservation_id = reservation_response.json()["reservation"]["id"]

#     # Start session first time
#     client.post(f"/sessions/reservations/{reservation_id}/start", headers=headers)

#     # Try to start again
#     response = client.post(
#         f"/sessions/reservations/{reservation_id}/start", headers=headers
#     )

#     assert response.status_code == 409
#     assert "Session already exists" in response.json()["detail"]


# # endregion


# # region POST /sessions/reservations/{reservation_id}/stop
# def test_stop_session_from_reservation_success(client_with_token):
#     """Test successfully stopping session from reservation without overtime"""
#     client, headers = client_with_token("user")
#     vehicle_id = get_last_vid(client_with_token)

#     # Create and start reservation session
#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": 1,
#         "start_date": (datetime.now() - timedelta(hours=2)).isoformat(),
#         "end_date": (datetime.now() + timedelta(hours=2)).isoformat(),
#     }
#     reservation_response = client.post(
#         "/reservations/create", json=reservation_data, headers=headers
#     )
#     reservation_id = reservation_response.json()["reservation"]["id"]

#     client.post(f"/sessions/reservations/{reservation_id}/start", headers=headers)

#     # Stop session
#     response = client.post(
#         f"/sessions/reservations/{reservation_id}/stop", headers=headers
#     )

#     assert response.status_code == 200
#     assert "stopped successfully" in response.json()["message"]


# def test_stop_session_from_reservation_not_found(client_with_token):
#     """Test stopping session from non-existent reservation"""
#     client, headers = client_with_token("user")

#     response = client.post("/sessions/reservations/99999/stop", headers=headers)

#     assert response.status_code == 404
#     assert "No active session found" in response.json()["detail"]


# def test_stop_session_from_reservation_already_stopped(client_with_token):
#     """Test stopping already stopped reservation session"""
#     client, headers = client_with_token("user")
#     vehicle_id = get_last_vid(client_with_token)

#     # Create and start/stop reservation session
#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": 1,
#         "start_date": (datetime.now() - timedelta(hours=2)).isoformat(),
#         "end_date": (datetime.now() + timedelta(hours=2)).isoformat(),
#     }
#     reservation_response = client.post(
#         "/reservations/create", json=reservation_data, headers=headers
#     )
#     reservation_id = reservation_response.json()["reservation"]["id"]

#     client.post(f"/sessions/reservations/{reservation_id}/start", headers=headers)
#     client.post(f"/sessions/reservations/{reservation_id}/stop", headers=headers)

#     # Try to stop again
#     response = client.post(
#         f"/sessions/reservations/{reservation_id}/stop", headers=headers
#     )

#     assert response.status_code == 409
#     assert "Session already stopped" in response.json()["detail"]


# def test_stop_session_from_reservation_no_authentication(client):
#     """Test stopping reservation session without authentication"""
#     response = client.post("/sessions/reservations/1/stop")

#     assert response.status_code == 401


# # endregion
