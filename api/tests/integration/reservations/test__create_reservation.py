import pytest
from datetime import datetime, timedelta
from api.tests.conftest import get_last_vid, get_last_pid


def test_create_reservation_success(client_with_token):
    """Test successfully creating a reservation"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=3)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Reservation created successfully"


def test_create_reservation_parking_lot_not_found(client_with_token):
    """Test creating reservation with non-existent parking lot"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)

    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=3)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": 99999,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "parking lot" in str(data["detail"]).lower()


def test_create_reservation_vehicle_not_found(client_with_token):
    """Test creating reservation with non-existent vehicle"""
    client, headers = client_with_token("superadmin")
    parking_lot_id = get_last_pid(client)

    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=3)

    reservation_data = {
        "vehicle_id": 99999,
        "parking_lot_id": parking_lot_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "vehicle" in str(data["detail"]).lower()


def test_create_reservation_no_authentication(client):
    """Test creating reservation without authentication"""
    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=3)

    reservation_data = {
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }

    response = client.post("/reservations/create", json=reservation_data)

    assert response.status_code == 401


def test_create_reservation_missing_fields(client_with_token):
    """Test creating reservation with missing required fields"""
    client, headers = client_with_token("superadmin")

    reservation_data = {
        "vehicle_id": 1,
        # Missing parking_lot_id, start_time, end_time
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    assert response.status_code == 422


def test_create_reservation_invalid_date_format(client_with_token):
    """Test creating reservation with invalid date format"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": "invalid-date",
        "end_time": "invalid-date",
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    assert response.status_code == 422


def test_create_reservation_start_time_in_past(client_with_token):
    """Test creating reservation with start time earlier than current time"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    start_time = datetime.now() - timedelta(hours=1)  # 1 hour in the past
    end_time = datetime.now() + timedelta(hours=1)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "start time" in str(data["detail"]).lower()
    assert "earlier than the current time" in str(data["detail"]).lower()


def test_create_reservation_start_time_after_end_time(client_with_token):
    """Test creating reservation where start time is later than end time"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    start_time = datetime.now() + timedelta(hours=5)  # Start after end
    end_time = datetime.now() + timedelta(hours=2)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "start time" in str(data["detail"]).lower()
    assert "later than the end time" in str(data["detail"]).lower()


def test_create_reservation_start_time_equals_end_time(client_with_token):
    """Test creating reservation where start time equals end time"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    same_time = datetime.now() + timedelta(hours=2)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": same_time.isoformat(),
        "end_time": same_time.isoformat(),
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "start time" in str(data["detail"]).lower()


def test_create_reservation_vehicle_already_reserved(client_with_token):
    """Test creating reservation when vehicle already has overlapping reservation (409)"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    # Create first reservation
    start_time1 = datetime.now() + timedelta(hours=10)
    end_time1 = datetime.now() + timedelta(hours=12)

    reservation_data1 = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": start_time1.isoformat(),
        "end_time": end_time1.isoformat(),
    }

    response1 = client.post(
        "/reservations/create", json=reservation_data1, headers=headers
    )
    assert response1.status_code == 200

    # Try to create overlapping reservation for same vehicle
    start_time2 = datetime.now() + timedelta(hours=11)  # Overlaps with first
    end_time2 = datetime.now() + timedelta(hours=13)

    reservation_data2 = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": start_time2.isoformat(),
        "end_time": end_time2.isoformat(),
    }

    response2 = client.post(
        "/reservations/create", json=reservation_data2, headers=headers
    )

    assert response2.status_code == 409
    data = response2.json()
    assert "detail" in data
    assert "overlap" in str(data["detail"]).lower()


# # region POST /admin/reservations
# def test_admin_create_reservation_success(client_with_token):
#     """Test admin successfully creating a reservation"""
#     client, headers = client_with_token("superadmin")
#     vehicle_id = get_last_vid(client_with_token)
#     parking_lot_id = get_last_pid(client)

#     start_time = datetime.now() + timedelta(hours=100)
#     end_time = datetime.now() + timedelta(hours=102)

#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": parking_lot_id,
#         "start_time": start_time.isoformat(),
#         "end_time": end_time.isoformat(),
#         "user_id": 1,
#     }

#     response = client.post(
#         "/admin/reservations", json=reservation_data, headers=headers
#     )

#     assert response.status_code == 201
#     data = response.json()
#     assert "message" in data
#     assert "reservation_id" in data


# def test_admin_create_reservation_as_lotadmin(client_with_token):
#     """Test lotadmin creating a reservation"""
#     client, headers = client_with_token("lotadmin")
#     vehicle_id = get_last_vid(client_with_token)
#     parking_lot_id = get_last_pid(client)

#     start_time = datetime.now() + timedelta(hours=110)
#     end_time = datetime.now() + timedelta(hours=112)

#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": parking_lot_id,
#         "start_time": start_time.isoformat(),
#         "end_time": end_time.isoformat(),
#         "user_id": 1,
#     }

#     response = client.post(
#         "/admin/reservations", json=reservation_data, headers=headers
#     )

#     assert response.status_code == 201


# def test_admin_create_reservation_as_regular_user(client_with_token):
#     """Test that regular user cannot use admin endpoint"""
#     client, headers = client_with_token("user")

#     start_time = datetime.now() + timedelta(hours=1)
#     end_time = datetime.now() + timedelta(hours=3)

#     reservation_data = {
#         "vehicle_id": 1,
#         "parking_lot_id": 1,
#         "start_time": start_time.isoformat(),
#         "end_time": end_time.isoformat(),
#         "user_id": 1,
#     }

#     response = client.post(
#         "/admin/reservations", json=reservation_data, headers=headers
#     )

#     assert response.status_code == 403


# def test_admin_create_reservation_no_authentication(client):
#     """Test creating reservation without authentication"""
#     start_time = datetime.now() + timedelta(hours=1)
#     end_time = datetime.now() + timedelta(hours=3)

#     reservation_data = {
#         "vehicle_id": 1,
#         "parking_lot_id": 1,
#         "start_time": start_time.isoformat(),
#         "end_time": end_time.isoformat(),
#         "user_id": 1,
#     }

#     response = client.post("/admin/reservations", json=reservation_data)

#     assert response.status_code == 401


# def test_admin_create_reservation_user_not_found(client_with_token):
#     """Test admin creating reservation for non-existent user"""
#     client, headers = client_with_token("superadmin")
#     vehicle_id = get_last_vid(client_with_token)
#     parking_lot_id = get_last_pid(client)

#     start_time = datetime.now() + timedelta(hours=1)
#     end_time = datetime.now() + timedelta(hours=3)

#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": parking_lot_id,
#         "start_time": start_time.isoformat(),
#         "end_time": end_time.isoformat(),
#         "user_id": 99999,
#     }

#     response = client.post(
#         "/admin/reservations", json=reservation_data, headers=headers
#     )

#     assert response.status_code == 404
#     assert "user" in response.json()["detail"].lower()


# def test_admin_create_reservation_vehicle_not_found(client_with_token):
#     """Test admin creating reservation with non-existent vehicle"""
#     client, headers = client_with_token("superadmin")
#     parking_lot_id = get_last_pid(client)

#     start_time = datetime.now() + timedelta(hours=1)
#     end_time = datetime.now() + timedelta(hours=3)

#     reservation_data = {
#         "vehicle_id": 99999,
#         "parking_lot_id": parking_lot_id,
#         "start_time": start_time.isoformat(),
#         "end_time": end_time.isoformat(),
#         "user_id": 1,
#     }

#     response = client.post(
#         "/admin/reservations", json=reservation_data, headers=headers
#     )

#     assert response.status_code == 404
#     assert "vehicle" in response.json()["detail"].lower()


# def test_admin_create_reservation_parking_lot_not_found(client_with_token):
#     """Test admin creating reservation with non-existent parking lot"""
#     client, headers = client_with_token("superadmin")
#     vehicle_id = get_last_vid(client_with_token)

#     start_time = datetime.now() + timedelta(hours=1)
#     end_time = datetime.now() + timedelta(hours=3)

#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": 99999,
#         "start_time": start_time.isoformat(),
#         "end_time": end_time.isoformat(),
#         "user_id": 1,
#     }

#     response = client.post(
#         "/admin/reservations", json=reservation_data, headers=headers
#     )

#     assert response.status_code == 404
#     assert "parking lot" in response.json()["detail"].lower()


# def test_admin_create_reservation_missing_user_id(client_with_token):
#     """Test admin creating reservation without user_id"""
#     client, headers = client_with_token("superadmin")
#     vehicle_id = get_last_vid(client_with_token)
#     parking_lot_id = get_last_pid(client)

#     start_time = datetime.now() + timedelta(hours=1)
#     end_time = datetime.now() + timedelta(hours=3)

#     reservation_data = {
#         "vehicle_id": vehicle_id,
#         "parking_lot_id": parking_lot_id,
#         "start_time": start_time.isoformat(),
#         "end_time": end_time.isoformat(),
#     }

#     response = client.post(
#         "/admin/reservations", json=reservation_data, headers=headers
#     )

#     assert response.status_code == 422


# # endregion