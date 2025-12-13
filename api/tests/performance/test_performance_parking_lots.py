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

@pytest.fixture
def seeded_parking_lots():
    lots = parking_lot_model.get_all_parking_lots()
    if len(lots) < 5:
        for i in range(5 - len(lots)):
            l = Parking_lot_create(
                name=f"BenchmarkLot{i+1}",
                location="TestCity",
                address=f"Address {i+1}",
                capacity=50,
                tariff=10.0,
                daytariff=100.0,
                lat=0.0,
                lng=0.0,
                status="open",
                closed_reason=None,
                closed_date=None,
            )
            parking_lot_model.create_parking_lot(l)


@pytest.fixture
def seeded_parking_lots():
    lots = parking_lot_model.get_all_parking_lots()
    if len(lots) < 5:
        for i in range(5 - len(lots)):
            l = Parking_lot_create(
                name=f"BenchmarkLot{i+1}",
                location="TestCity",
                address=f"Address {i+1}",
                capacity=50,
                tariff=10.0,
                daytariff=100.0,
                lat=0.0,
                lng=0.0,
                status="open",
                closed_reason=None,
                closed_date=None,
            )
            parking_lot_model.create_parking_lot(l)


@pytest.fixture
def seeded_sessions():
    lots = parking_lot_model.get_all_parking_lots()
    lot_id = lots[0].id

    sessions = parking_lot_model.get_all_sessions_by_lid(lot_id)
    if len(sessions) < 5:
        for i in range(5 - len(lots)):
            l = SessionCreate(
                name=f"BenchmarkLot{i+1}",
                location="TestCity",
                address=f"Address {i+1}",
                capacity=50,
                tariff=10.0,
                daytariff=100.0,
                lat=0.0,
                lng=0.0,
                status="open",
                closed_reason=None,
                closed_date=None,
            )
            parking_lot_model.create_parking_lot(l)


@pytest.mark.benchmark(group="parking_lots")
def test_get_all_parking_lots_performance(benchmark, client_with_token, seeded_parking_lots):
    client, headers = client_with_token("superadmin")

    def get_all_lots():
        return client.get("/parking-lots/", headers=headers)

    result = benchmark(get_all_lots)
    assert result.status_code == 200
    assert isinstance(result.json(), list)


@pytest.mark.benchmark(group="parking_lots")
def test_get_sessions_performance(benchmark, client_with_token, seeded_parking_lots):
    client, headers = client_with_token("superadmin")
    
    # Pick a lot id for testing
    lots = parking_lot_model.get_all_parking_lots()
    lot_id = lots[0].id

    def get_sessions():
        return client.get(f"/parking-lots/{lot_id}/sessions", headers=headers)

    result = benchmark(get_sessions)
    assert result.status_code in (200, 204)  # 204 if no sessions exist
    # optionally check JSON only if sessions exist