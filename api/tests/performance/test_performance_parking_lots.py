import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.models.parking_lot_model import ParkingLotModel
from api.datatypes.parking_lot import Parking_lot_create
from api.models.session_model import SessionModel
from api.datatypes.session import SessionCreate

client = TestClient(app)
parking_lot_model = ParkingLotModel()
session_model = SessionModel()


@pytest.mark.benchmark(group="parking_lots")
def test_get_all_parking_lots_performance(benchmark, client_with_token):
    client, headers = client_with_token("superadmin")

    def get_all_lots():
        return client.get("/parking-lots/", headers=headers)

    result = benchmark(get_all_lots)
    assert result.status_code == 200


@pytest.mark.benchmark(group="parking_lots")
def test_get_sessions_performance(benchmark, client_with_token, seeded_parking_lots):
    client, headers = client_with_token("superadmin")
    

    lots = parking_lot_model.get_all_parking_lots()
    lot_id = lots[0].id

    def get_sessions():
        return client.get(f"/parking-lots/{lot_id}/sessions", headers=headers)

    result = benchmark(get_sessions)
    assert result.status_code in (200)