import pytest
from unittest.mock import patch, MagicMock, mock_open
from api.data_converter import DataConverter

def test_read_data_file_found(monkeypatch):
    # Mock os.path.exists to always return True
    monkeypatch.setattr("os.path.exists", lambda path: True)
    # Mock open to return a JSON string
    test_json = '[{"username": "testuser"}]'
    monkeypatch.setattr("builtins.open", mock_open(read_data=test_json))
    # Mock json.load to load our test data
    with patch("json.load", return_value=[{"username": "testuser"}]):
        dc = DataConverter()
        data = dc.read_data("users")
        assert data == [{"username": "testuser"}]

def test_read_data_file_not_found(monkeypatch):
    monkeypatch.setattr("os.path.exists", lambda path: False)
    dc = DataConverter()
    with pytest.raises(FileNotFoundError):
        dc.read_data("users")

def test_insert_user_inserts_and_commits(monkeypatch):
    dc = DataConverter()
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    dc.connection = mock_conn
    users = [{"username": "test", "password": "pw", "name": "n", "email": "e", "phone": "p", "birth_year": 2000}]
    mock_cursor.fetchone.return_value = [0]
    dc.insert_user(users)
    assert mock_cursor.execute.call_count >= 2
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()

# def test_add_super_admin_creates_if_not_exists(monkeypatch):
#     dc = DataConverter()
#     mock_cursor = MagicMock()
#     mock_conn = MagicMock()
#     mock_conn.cursor.return_value = mock_cursor
#     dc.connection = mock_conn
#     mock_cursor.fetchone.return_value = None  # No superadmin exists
#     with patch("api.data_converter.hash_string", return_value="hashed"):
#         dc.add_super_admin()
#     assert mock_cursor.execute.call_count >= 2
#     mock_conn.commit.assert_called()

def test_add_super_admin_skips_if_exists(monkeypatch):
    dc = DataConverter()
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    dc.connection = mock_conn
    mock_cursor.fetchone.return_value = (1,)  # Superadmin exists
    dc.add_super_admin()
    # Should not insert or commit
    assert mock_cursor.execute.call_count == 1

def test_read_session_data_merges_dicts(monkeypatch):
    dc = DataConverter()
    # Mock os.path.exists to True for first file, False for the rest
    monkeypatch.setattr("os.path.exists", lambda path: "p1-sessions.json" in path)
    # Mock open to return a dict for the first file
    test_json = '{"a": 1}'
    monkeypatch.setattr("builtins.open", mock_open(read_data=test_json))
    with patch("json.load", return_value={"a": 1}):
        pdata = dc.read_session_data()
        assert pdata == {"a": 1}

def test_read_session_data_skips_non_dict(monkeypatch):
    dc = DataConverter()
    monkeypatch.setattr("os.path.exists", lambda path: "p1-sessions.json" in path)
    monkeypatch.setattr("builtins.open", mock_open(read_data="[]"))
    with patch("json.load", return_value=[1, 2, 3]):
        pdata = dc.read_session_data()
        assert pdata == {}

def test_insert_vehicle_inserts_and_commits(monkeypatch):
    dc = DataConverter()
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    dc.connection = mock_conn
    vehicles = [{
        "user_id": 1,
        "license_plate": "XX-YY-01",
        "make": "Ford",
        "model": "Fiesta",
        "color": "blue",
        "year": 2020,
        "created_at": "2020-01-01"
    }]
    dc.insert_vehicle(vehicles)
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    assert mock_cursor.execute.call_count == 1

def test_insert_parking_lots_inserts_and_commits(monkeypatch):
    dc = DataConverter()
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    dc.connection = mock_conn
    lots = {
        "1": {
            "name": "Lot1",
            "location": "Loc1",
            "address": "Addr1",
            "capacity": 10,
            "reserved": 2,
            "tariff": 1.5,
            "daytariff": 10.0,
            "created_at": "2020-01-01",
            "coordinates": {"lat": 1.0, "lng": 2.0}
        }
    }
    dc.insert_parking_lots(lots)
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    assert mock_cursor.execute.call_count == 1

def test_insert_user_handles_existing_user(monkeypatch):
    dc = DataConverter()
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    dc.connection = mock_conn
    users = [{"username": "test", "password": "pw", "name": "n", "email": "e", "phone": "p", "birth_year": 2000}]
    mock_cursor.fetchone.return_value = [1]  # User already exists
    dc.insert_user(users)
    # is_active should be False, but still inserts
    assert mock_cursor.execute.call_count >= 2
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()

def test_insert_payment_inserts_and_commits(monkeypatch):
    dc = DataConverter()
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    dc.connection = mock_conn
    # Mock user mapping
    mock_cursor.fetchall.return_value = [(1, "testuser")]
    payments = [{
        "initiator": "testuser",
        "transaction": "tx1",
        "amount": "10.5",
        "completed": True,
        "hash": "abc",
        "t_data": {
            "method": "ideal",
            "issuer": "ING",
            "bank": "ING",
            "date": "2023-01-01 12:00:00"
        }
    }]
    with patch("api.data_converter.execute_values") as mock_exec_values:
        dc.insert_payment(payments, batch_size=1)
        mock_exec_values.assert_called()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()

def test_insert_reservations_inserts_and_commits(monkeypatch):
    dc = DataConverter()
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    dc.connection = mock_conn
    reservations = [{
        "vehicle_id": 1,
        "user_id": 2,
        "parking_lot_id": 3,
        "start_time": "2023-01-01T10:00:00Z",
        "end_time": "2023-01-01T12:00:00Z",
        "status": "active",
        "created_at": "2023-01-01T09:00:00Z",
        "cost": 5.0
    }]
    dc.insert_reservations(reservations)
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    assert mock_cursor.execute.call_count == 1

# def test_insert_sessions_inserts_and_commits(monkeypatch):
#     dc = DataConverter()
#     mock_cursor = MagicMock()
#     mock_conn = MagicMock()
#     mock_conn.cursor.return_value = mock_cursor
#     # Mock user and vehicle fetches
#     mock_cursor.fetchall.side_effect = [
#         [(1, "testuser")],  # users
#         [(2, "XX-YY-01")]   # vehicles
#     ]
#     dc.connection = mock_conn
#     sessions = {
#         "1": {
#             "parking_lot_id": 1,
#             "user": "testuser",
#             "licenseplate": "XX-YY-01",
#             "started": "2023-01-01T10:00:00Z",
#             "stopped": "2023-01-01T12:00:00Z",
#             "cost": 5.0
#         }
#     }
#     dc.insert_sessions(sessions)
#     mock_conn.commit.assert_called_once()
#     mock_cursor.close.assert_called_once()
#     assert mock_cursor.execute.call_count == 1

def test_convert_aborts_on_missing_users(monkeypatch):
    dc = DataConverter()
    # Mock read_data to return None for users
    dc.read_data = MagicMock(side_effect=[None])
    dc.insert_user = MagicMock()
    dc.insert_vehicle = MagicMock()
    dc.insert_parking_lots = MagicMock()
    dc.insert_payment = MagicMock()
    dc.insert_reservations = MagicMock()
    dc.read_session_data = MagicMock()
    dc.insert_sessions = MagicMock()
    dc.convert()
    dc.insert_user.assert_not_called()
    dc.insert_vehicle.assert_not_called()

def test_convert_full_flow(monkeypatch):
    dc = DataConverter()
    # Mock all read_data and insert methods to simulate full flow
    dc.read_data = MagicMock(side_effect=[
        [{"username": "a"}],  # users
        [{"user_id": 1, "license_plate": "X", "make": "A", "model": "B", "color": "C", "year": 2020, "created_at": "2020-01-01"}],  # vehicles
        {"1": {"name": "Lot", "location": "Loc", "address": "Addr", "capacity": 1, "reserved": 0, "tariff": 1.0, "daytariff": 10.0, "created_at": "2020-01-01", "coordinates": {"lat": 1.0, "lng": 2.0}}},  # parking-lots
        [{"initiator": "a", "transaction": "t", "amount": "1", "completed": True, "hash": "h", "t_data": {"method": "m", "issuer": "i", "bank": "b", "date": "2020-01-01 00:00:00"}}],  # payments
        [{"vehicle_id": 1, "user_id": 1, "parking_lot_id": 1, "start_time": "2020-01-01T10:00:00Z", "end_time": "2020-01-01T12:00:00Z", "status": "active", "created_at": "2020-01-01T09:00:00Z", "cost": 5.0}],  # reservations
    ])
    dc.insert_user = MagicMock()
    dc.insert_vehicle = MagicMock()
    dc.insert_parking_lots = MagicMock()
    dc.insert_payment = MagicMock()
    dc.insert_reservations = MagicMock()
    dc.read_session_data = MagicMock(return_value={"1": {}})
    dc.insert_sessions = MagicMock()
    dc.convert()
    dc.insert_user.assert_called_once()
    dc.insert_vehicle.assert_called_once()
    dc.insert_parking_lots.assert_called_once()
    dc.insert_payment.assert_called_once()
    dc.insert_reservations.assert_called_once()
    dc.insert_sessions.assert_called_once()

def test_insert_vehicle_handles_exception(monkeypatch, caplog):
    dc = DataConverter()
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    dc.connection = mock_conn
    # Geef een vehicle met een onjuiste datum
    vehicles = [{
        "user_id": 1,
        "license_plate": "XX-YY-01",
        "make": "Ford",
        "model": "Fiesta",
        "color": "blue",
        "year": 2020,
        "created_at": "invalid-date"
    }]
    dc.insert_vehicle(vehicles)
    # Er moet een error gelogd zijn
    assert any("Failed to insert vehicle" in record.message for record in caplog.records)

def test_insert_parking_lots_handles_exception(monkeypatch, caplog):
    dc = DataConverter()
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    dc.connection = mock_conn
    lots = {
        "1": {
            "name": "Lot1",
            "location": "Loc1",
            "address": "Addr1",
            "capacity": 10,
            "reserved": 2,
            "tariff": 1.5,
            "daytariff": 10.0,
            "created_at": "invalid-date",
            "coordinates": {"lat": 1.0, "lng": 2.0}
        }
    }
    dc.insert_parking_lots(lots)
    assert any("Failed to insert parking lot" in record.message for record in caplog.records)

def test_insert_payment_handles_invalid_date(monkeypatch, caplog):
    dc = DataConverter()
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    dc.connection = mock_conn
    mock_cursor.fetchall.return_value = [(1, "testuser")]
    payments = [{
        "initiator": "testuser",
        "transaction": "tx1",
        "amount": "10.5",
        "completed": True,
        "hash": "abc",
        "t_data": {
            "method": "ideal",
            "issuer": "ING",
            "bank": "ING",
            "date": "not-a-date"
        }
    }]
    with patch("api.data_converter.execute_values"):
        dc.insert_payment(payments, batch_size=1)
    assert any("Invalid date format" in record.message for record in caplog.records)

def test_insert_sessions_handles_exception(monkeypatch, caplog):
    dc = DataConverter()
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    # Mock user and vehicle fetches
    mock_cursor.fetchall.side_effect = [
        [(1, "testuser")],  # users
        [(2, "XX-YY-01")]   # vehicles
    ]
    dc.connection = mock_conn
    sessions = {
        "1": {
            "parking_lot_id": 1,
            "user": "testuser",
            "licenseplate": "XX-YY-01",
            "started": "not-a-date",
            "stopped": "2023-01-01T12:00:00Z",
            "cost": 5.0
        }
    }
    dc.insert_sessions(sessions)
    assert any("Failed to insert session" in record.message for record in caplog.records)

def test_insert_payment_warns_on_unknown_user(monkeypatch, caplog):
    dc = DataConverter()
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    dc.connection = mock_conn
    mock_cursor.fetchall.return_value = [(1, "testuser")]
    payments = [{
        "initiator": "unknownuser",
        "transaction": "tx1",
        "amount": "10.5",
        "completed": True,
        "hash": "abc",
        "t_data": {
            "method": "ideal",
            "issuer": "ING",
            "bank": "ING",
            "date": "2023-01-01 12:00:00"
        }
    }]
    with patch("api.data_converter.execute_values"):
        dc.insert_payment(payments, batch_size=1)
    assert any("could not be uniquely matched" in record.message for record in caplog.records)

def test_insert_user_handles_db_exception(monkeypatch, caplog):
    dc = DataConverter()
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    dc.connection = mock_conn
    users = [{"username": "fail", "password": "pw", "name": "n", "email": "e", "phone": "p", "birth_year": 2000}]
    # Force an exception on insert
    mock_cursor.execute.side_effect = [None, Exception("DB error")]
    with pytest.raises(Exception):
        dc.insert_user(users)
    # Exception should propagate, but also be logged if caught in production

# def test_add_super_admin_handles_exception(monkeypatch, caplog):
#     dc = DataConverter()
#     mock_cursor = MagicMock()
#     mock_conn = MagicMock()
#     mock_conn.cursor.return_value = mock_cursor
#     dc.connection = mock_conn
#     mock_cursor.fetchone.return_value = None  # No superadmin exists
#     # Force an exception on insert
#     mock_cursor.execute.side_effect = Exception("DB error")
#     with patch("api.data_converter.hash_string", return_value="hashed"):
#         dc.add_super_admin()
#     assert "Failed to create superadmin" in caplog.text or "Failed to create superadmin" in caplog.messages

def test_insert_reservations_handles_invalid_dates(monkeypatch, caplog):
    dc = DataConverter()
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    dc.connection = mock_conn
    reservations = [{
        "vehicle_id": 1,
        "user_id": 2,
        "parking_lot_id": 3,
        "start_time": "not-a-date",
        "end_time": "not-a-date",
        "status": "active",
        "created_at": "not-a-date",
        "cost": 5.0
    }]
    dc.insert_reservations(reservations)
    assert any("Failed to insert reservation" in record.message for record in caplog.records)

def test_insert_sessions_warns_on_multiple_users(monkeypatch, caplog):
    dc = DataConverter()
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    # Mock user fetch: two users with same username
    mock_cursor.fetchall.side_effect = [
        [(1, "dupuser"), (2, "dupuser")],  # users
        [(3, "XX-YY-01")]                  # vehicles
    ]
    dc.connection = mock_conn
    sessions = {
        "1": {
            "parking_lot_id": 1,
            "user": "dupuser",
            "licenseplate": "XX-YY-01",
            "started": "2023-01-01T10:00:00Z",
            "stopped": "2023-01-01T12:00:00Z",
            "cost": 5.0
        }
    }
    dc.insert_sessions(sessions)
    assert any("Multiple users found for username" in record.message for record in caplog.records)

def test_insert_sessions_warns_on_no_user(monkeypatch, caplog):
    dc = DataConverter()
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    # Mock user fetch: no users
    mock_cursor.fetchall.side_effect = [
        [],  # users
        [(3, "XX-YY-01")]  # vehicles
    ]
    dc.connection = mock_conn
    sessions = {
        "1": {
            "parking_lot_id": 1,
            "user": "nouser",
            "licenseplate": "XX-YY-01",
            "started": "2023-01-01T10:00:00Z",
            "stopped": "2023-01-01T12:00:00Z",
            "cost": 5.0
        }
    }
    dc.insert_sessions(sessions)
    assert any("No user found for username" in record.message for record in caplog.records)