from unittest.mock import patch
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


# Tests voor DELETE /reservations/delete/{reservation_id}
def test_delete_reservation_success(client_with_token):
    client, headers = client_with_token("user")

    # Eerst een reservatie aanmaken
    reservation_data = {
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_date": "2025-12-10T09:00:00",
        "end_date": "2025-12-10T18:00:00",
    }
    create_response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    if create_response.status_code in [200, 201]:
        reservation_id = create_response.json().get("reservation_id")
        response = client.delete(
            f"/reservations/delete/{reservation_id}", headers=headers
        )
        assert response.status_code == 200


def test_delete_reservation_unauthorized(client):
    response = client.delete("/reservations/delete/1")
    assert response.status_code == 401


def test_delete_reservation_not_found(client_with_token):
    client, headers = client_with_token("user")
    response = client.delete("/reservations/delete/99999", headers=headers)
    assert response.status_code == 404


def test_delete_reservation_wrong_owner(client_with_token):
    client, headers = client_with_token("user")
    # Assuming reservation 2 belongs to another user
    response = client.delete("/reservations/delete/2", headers=headers)
    assert response.status_code == 403


def test_delete_reservation_invalid_id(client_with_token):
    client, headers = client_with_token("user")
    response = client.delete("/reservations/delete/invalid_id", headers=headers)
    assert response.status_code == 422


def test_delete_reservation_negative_id(client_with_token):
    client, headers = client_with_token("user")
    response = client.delete("/reservations/delete/-1", headers=headers)
    assert response.status_code in [404, 422]


@patch(
    "api.models.reservation_model.Reservation_model.delete_reservation",
    return_value=False,
)
def test_delete_reservation_server_error(mock_delete, client_with_token):
    client, headers = client_with_token("user")

    # Eerst een reservatie aanmaken
    reservation_data = {
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_date": "2025-12-10T09:00:00",
        "end_date": "2025-12-10T18:00:00",
    }
    create_response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    if create_response.status_code in [200, 201]:
        reservation_id = create_response.json().get("reservation_id")
        response = client.delete(
            f"/reservations/delete/{reservation_id}", headers=headers
        )
        assert response.status_code == 500


# Tests voor DELETE /admin/reservations/{reservation_id}
def test_admin_delete_reservation_success(client_with_token):
    admin_client, headers = client_with_token("admin")

    # Eerst een reservatie aanmaken
    reservation_data = {
        "user_id": 1,
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_time": "2025-12-10T09:00:00",
        "end_time": "2025-12-10T18:00:00",
        "status": "confirmed",
        "cost": 20,
    }
    create_response = admin_client.post(
        "/admin/reservations", json=reservation_data, headers=headers
    )

    if create_response.status_code == 201:
        reservation_id = create_response.json().get("reservation_id")
        response = admin_client.delete(
            f"/admin/reservations/{reservation_id}", headers=headers
        )
        assert response.status_code == 200


def test_admin_delete_reservation_unauthorized(client):
    response = client.delete("/admin/reservations/1")
    assert response.status_code == 401


def test_admin_delete_reservation_forbidden(client_with_token):
    user_client, headers = client_with_token("user")
    response = user_client.delete("/admin/reservations/1", headers=headers)
    assert response.status_code == 403


def test_admin_delete_reservation_not_found(client_with_token):
    admin_client, headers = client_with_token("admin")
    response = admin_client.delete("/admin/reservations/99999", headers=headers)
    assert response.status_code == 404


def test_admin_delete_reservation_invalid_id(client_with_token):
    admin_client, headers = client_with_token("admin")
    response = admin_client.delete("/admin/reservations/invalid_id", headers=headers)
    assert response.status_code == 422


def test_admin_delete_reservation_negative_id(client_with_token):
    admin_client, headers = client_with_token("admin")
    response = admin_client.delete("/admin/reservations/-1", headers=headers)
    assert response.status_code in [404, 422]


@patch(
    "api.models.reservation_model.Reservation_model.delete_reservation",
    return_value=False,
)
def test_admin_delete_reservation_server_error(mock_delete, client_with_token):
    admin_client, headers = client_with_token("admin")

    # Eerst een reservatie aanmaken
    reservation_data = {
        "user_id": 1,
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_time": "2025-12-10T09:00:00",
        "end_time": "2025-12-10T18:00:00",
        "status": "confirmed",
        "cost": 20,
    }
    create_response = admin_client.post(
        "/admin/reservations", json=reservation_data, headers=headers
    )

    if create_response.status_code == 201:
        reservation_id = create_response.json().get("reservation_id")
        response = admin_client.delete(
            f"/admin/reservations/{reservation_id}", headers=headers
        )
        assert response.status_code == 500
