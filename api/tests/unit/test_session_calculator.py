from datetime import datetime, timedelta
from api.session_calculator import (
    calculate_price,
    generate_payment_hash,
    generate_transaction_validation_hash,
)


class MockParkingLot:
    def __init__(self, tariff, daytariff):
        self.tariff = tariff
        self.daytariff = daytariff


class MockSession:
    def __init__(self, started, stopped=None):
        self.started = started
        self.stopped = stopped


def test_calculate_price_short_session_free():
    parking_lot = MockParkingLot(tariff=2.0, daytariff=10.0)
    now = datetime.now()
    session = MockSession(started=now - timedelta(minutes=2), stopped=now)
    price = calculate_price(parking_lot, session, None)
    assert price == 0


def test_calculate_price_hourly_tariff():
    parking_lot = MockParkingLot(tariff=2.0, daytariff=10.0)
    now = datetime.now()
    session = MockSession(started=now - timedelta(hours=1, minutes=10),
                          stopped=now)
    price = calculate_price(parking_lot, session, None)
    assert price == 4.0  # 2 hours * 2.0


def test_calculate_price_day_tariff():
    parking_lot = MockParkingLot(tariff=2.0, daytariff=10.0)
    now = datetime.now()
    session = MockSession(started=now - timedelta(hours=25), stopped=now)
    price = calculate_price(parking_lot, session, None)
    assert price == 20.0  # 2 days * 10.0


def test_calculate_price_caps_at_daytariff():
    parking_lot = MockParkingLot(tariff=5.0, daytariff=10.0)
    now = datetime.now()
    session = MockSession(started=now - timedelta(hours=3), stopped=now)
    price = calculate_price(parking_lot, session, None)
    assert price == 10.0  # 3*5=15 > daytariff, so cap at 10


def test_generate_payment_hash_is_same():
    sid = "123"
    licenseplate = "ABC-123"
    hash1 = generate_payment_hash(sid, licenseplate)
    hash2 = generate_payment_hash(sid, licenseplate)
    assert hash1 == hash2


def test_generate_payment_hash_differs_for_different_inputs():
    hash1 = generate_payment_hash("123", "ABC-123")
    hash2 = generate_payment_hash("124", "ABC-123")
    assert hash1 != hash2


def test_generate_transaction_validation_hash_is_uuid():
    hash1 = generate_transaction_validation_hash()
    hash2 = generate_transaction_validation_hash()
    assert hash1 != hash2
