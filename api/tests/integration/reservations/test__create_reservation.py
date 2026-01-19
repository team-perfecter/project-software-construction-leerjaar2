# from unittest.mock import patch
# from fastapi.testclient import TestClient
# from api.main import app
# from api.tests.conftest import get_last_pid, get_last_vid

# client = TestClient(app)


# def test_create_reservation_with_superadmin(client_with_token):
#     """Creates a new reservation as a superadmin and checks the response."""
#     client, headers = client_with_token("superadmin")
#     parking_lot_id = get_last_pid(client)
#     vehicle_id = get_last_vid(client_with_token)

#     fake_reservation = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": parking_lot_id,
#         "start_time": "2027-12-10T09:00:00",
#         "end_time": "2027-12-10T18:00:00"
#     }

#     response = client.post("/reservations/create", json=fake_reservation, headers=headers)
#     assert response.status_code == 200


# def test_create_reservation_overlap(client_with_token):
#     """Creates a new reservation as a superadmin and checks the response."""
#     client, headers = client_with_token("superadmin")
#     parking_lot_id = get_last_pid(client)
#     vehicle_id = get_last_vid(client_with_token)

#     fake_reservation = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": parking_lot_id,
#         "start_time": "2027-12-10T09:00:00",
#         "end_time": "2027-12-10T18:00:00"
#     }

#     client.post("/reservations/create", json=fake_reservation, headers=headers)
#     response = client.post("/reservations/create", json=fake_reservation, headers=headers)
#     assert response.status_code == 409


# def test_create_reservation_with_superadmin_vehicle_nonexistent(client_with_token):
#     """Creates a new reservation as a superadmin and checks the response."""
#     client, headers = client_with_token("superadmin")
#     parking_lot_id = get_last_pid(client)
#     fake_reservation = {
#         "vehicle_id": 999999999,
#         "parking_lot_id": parking_lot_id,
#         "start_time": "2027-12-10T09:00:00",
#         "end_time": "2027-12-10T18:00:00"
#     }

#     response = client.post("/reservations/create", json=fake_reservation, headers=headers)
#     assert response.status_code == 404


# def test_create_reservation_with_superadmin_lot_nonexistent(client_with_token):
#     """Creates a new reservation as a superadmin and checks the response."""
#     client, headers = client_with_token("superadmin")
#     vehicle_id = get_last_vid(client_with_token)
#     fake_reservation = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": 999999,
#         "start_time": "2027-12-10T09:00:00",
#         "end_time": "2027-12-10T18:00:00"
#     }

#     response = client.post("/reservations/create", json=fake_reservation, headers=headers)
#     assert response.status_code == 404


# def test_create_reservation_start_in_the_past(client_with_token):
#     """Creates a new reservation as a superadmin and checks the response."""
#     client, headers = client_with_token("superadmin")
#     parking_lot_id = get_last_pid(client)
#     vehicle_id = get_last_vid(client_with_token)

#     fake_reservation = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": parking_lot_id,
#         "start_time": "2025-12-10T09:00:00",
#         "end_time": "2027-11-10T18:00:00"
#     }

#     response = client.post("/reservations/create", json=fake_reservation, headers=headers)
#     assert response.status_code == 400


# def test_create_reservation_with_start_after_end(client_with_token):
#     """Creates a new reservation as a superadmin and checks the response."""
#     client, headers = client_with_token("superadmin")
#     parking_lot_id = get_last_pid(client)
#     vehicle_id = get_last_vid(client_with_token)

#     fake_reservation = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": parking_lot_id,
#         "start_time": "2027-12-10T09:00:00",
#         "end_time": "2027-11-10T18:00:00"
#     }

#     response = client.post("/reservations/create", json=fake_reservation, headers=headers)
#     assert response.status_code == 400