# import pytest
# from datetime import datetime, timedelta


# def test_create_reservation_success(client_with_token):
#     """Test successful reservation creation"""
#     client, headers = client_with_token("user")
    
#     # Get existing vehicle and parking lot IDs from fixtures
#     vehicle_response = client.get("/vehicles", headers=headers)
#     vehicle_id = vehicle_response.json()[0]["id"]
    
#     parking_response = client.get("/parking-lots/", headers=headers)
#     parking_lot_id = parking_response.json()[0]["id"]
    
#     # Create reservation with future dates
#     reservation_data = {
#         "parking_lot_id": parking_lot_id,
#         "vehicle_id": vehicle_id,
#         "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
#         "end_date": (datetime.now() + timedelta(days=2)).isoformat()
#     }
    
#     response = client.post("/reservations/create", json=reservation_data, headers=headers)
    
#     assert response.status_code == 201
#     assert "reservation created" in response.json()["detail"]["message"]


# def test_create_reservation_nonexistent_parking_lot(client_with_token):
#     """Test creating reservation with non-existent parking lot"""
#     client, headers = client_with_token("user")
    
#     vehicle_response = client.get("/vehicles", headers=headers)
#     vehicle_id = vehicle_response.json()[0]["id"]
    
#     reservation_data = {
#         "parking_lot_id": 99999,  # Non-existent ID
#         "vehicle_id": vehicle_id,
#         "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
#         "end_date": (datetime.now() + timedelta(days=2)).isoformat()
#     }
    
#     response = client.post("/reservations/create", json=reservation_data, headers=headers)
    
#     assert response.status_code == 404
#     assert "Parking lot does not exist" in response.json()["detail"]["message"]


# def test_create_reservation_nonexistent_vehicle(client_with_token):
#     """Test creating reservation with non-existent vehicle"""
#     client, headers = client_with_token("user")
    
#     parking_response = client.get("/parking-lots/", headers=headers)
#     parking_lot_id = parking_response.json()[0]["id"]
    
#     reservation_data = {
#         "parking_lot_id": parking_lot_id,
#         "vehicle_id": 99999,  # Non-existent ID
#         "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
#         "end_date": (datetime.now() + timedelta(days=2)).isoformat()
#     }
    
#     response = client.post("/reservations/create", json=reservation_data, headers=headers)
    
#     assert response.status_code == 404
#     assert "Vehicle does not exist" in response.json()["detail"]["message"]


# def test_create_reservation_start_date_in_past(client_with_token):
#     """Test creating reservation with start date in the past"""
#     client, headers = client_with_token("user")
    
#     vehicle_response = client.get("/vehicles", headers=headers)
#     vehicle_id = vehicle_response.json()[0]["id"]
    
#     parking_response = client.get("/parking-lots/", headers=headers)
#     parking_lot_id = parking_response.json()[0]["id"]
    
#     reservation_data = {
#         "parking_lot_id": parking_lot_id,
#         "vehicle_id": vehicle_id,
#         "start_date": (datetime.now() - timedelta(days=1)).isoformat(),  # Past date
#         "end_date": (datetime.now() + timedelta(days=2)).isoformat()
#     }
    
#     response = client.post("/reservations/create", json=reservation_data, headers=headers)
    
#     assert response.status_code == 403
#     assert "start date cannot be earlier than the current date" in response.json()["detail"]["message"]


# def test_create_reservation_end_date_before_start_date(client_with_token):
#     """Test creating reservation with end date before start date"""
#     client, headers = client_with_token("user")
    
#     vehicle_response = client.get("/vehicles", headers=headers)
#     vehicle_id = vehicle_response.json()[0]["id"]
    
#     parking_response = client.get("/parking-lots/", headers=headers)
#     parking_lot_id = parking_response.json()[0]["id"]
    
#     start_date = datetime.now() + timedelta(days=2)
#     end_date = datetime.now() + timedelta(days=1)
    
#     reservation_data = {
#         "parking_lot_id": parking_lot_id,
#         "vehicle_id": vehicle_id,
#         "start_date": start_date.isoformat(),
#         "end_date": end_date.isoformat()  # Before start date
#     }
    
#     response = client.post("/reservations/create", json=reservation_data, headers=headers)
    
#     assert response.status_code == 403
#     assert "start date cannot be later than the end date" in response.json()["detail"]["message"]


# def test_create_reservation_start_equals_end_date(client_with_token):
#     """Test creating reservation where start date equals end date"""
#     client, headers = client_with_token("user")
    
#     vehicle_response = client.get("/vehicles", headers=headers)
#     vehicle_id = vehicle_response.json()[0]["id"]
    
#     parking_response = client.get("/parking-lots/", headers=headers)
#     parking_lot_id = parking_response.json()[0]["id"]
    
#     same_date = (datetime.now() + timedelta(days=1)).isoformat()
    
#     reservation_data = {
#         "parking_lot_id": parking_lot_id,
#         "vehicle_id": vehicle_id,
#         "start_date": same_date,
#         "end_date": same_date  # Same as start date
#     }
    
#     response = client.post("/reservations/create", json=reservation_data, headers=headers)
    
#     assert response.status_code == 403
#     assert "start date cannot be later than the end date" in response.json()["detail"]["message"]


# def test_create_reservation_unauthenticated(client):
#     """Test creating reservation without authentication"""
#     reservation_data = {
#         "parking_lot_id": 1,
#         "vehicle_id": 1,
#         "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
#         "end_date": (datetime.now() + timedelta(days=2)).isoformat()
#     }
    
#     response = client.post("/reservations/create", json=reservation_data)
    
#     assert response.status_code == 401


# @pytest.mark.parametrize("role", ["user", "admin", "superadmin", "paymentadmin"])
# def test_create_reservation_different_roles(client_with_token, role):
#     """Test that all user roles can create reservations"""
#     client, headers = client_with_token(role)
    
#     vehicle_response = client.get("/vehicles", headers=headers)
#     if vehicle_response.status_code == 200 and vehicle_response.json():
#         vehicle_id = vehicle_response.json()[0]["id"]
#     else:
#         pytest.skip(f"No vehicles available for role {role}")
    
#     parking_response = client.get("/parking-lots/", headers=headers)
#     parking_lot_id = parking_response.json()[0]["id"]
    
#     reservation_data = {
#         "parking_lot_id": parking_lot_id,
#         "vehicle_id": vehicle_id,
#         "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
#         "end_date": (datetime.now() + timedelta(days=2)).isoformat()
#     }
    
#     response = client.post("/reservations/create", json=reservation_data, headers=headers)
    
#     assert response.status_code == 201