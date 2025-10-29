from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
import jwt
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from ../../app import app

'''
payments will be in a separate class. the input of this class will be the authorization token of the user.
each endpoint will check if the token is valid. if not valid, return 401
the validity of a token is checked in the get_user(token: str = Depends(oauth2_scheme)) function.
db_create_payment(data) is a function that creates a new payment.
db_refund_payment(data) is a function that refunds a payment (creates a negative transaction).
'''

client = TestClient(app)

@dataclass
class Payment:
    user_id: int
    amount: float
    method: str
    status: str
    created_at: str

payments: list[Payment] = []

def fake_create_payment(payment: Payment) -> None:
    payments.append(payment)

def fake_refund_payment(payment: Payment) -> None:
    payment.amount = -abs(payment.amount)
    payments.append(payment)

def create_test_token(username: str) -> str:
    expire: datetime = datetime.utcnow() + timedelta(minutes=30)
    token: str = jwt.encode({"sub": username, "exp": expire}, "SECRET_KEY", algorithm="HS256")
    return token

token: str = create_test_token("alice")
valid_header: dict[str, str] = {"Authorization": f"Bearer {token}"}
invalid_header: dict[str, str] = {"Authorization": "Bearer invalid"}

'''
Test creating a payment when authorized.
'''
@patch("../../controllers/payment_controller.db_create_payment", side_effect=fake_create_payment)
def test_create_payment_when_authorized() -> None:
    data: Payment = Payment(1, 12.5, "credit_card", "completed", datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"))
    response = client.post("/payments", headers=valid_header, json=asdict(data))
    assert response.status_code == 201
    assert len(payments) == 1
    assert payments[0].amount == 12.5
    payments.clear()

'''
Test creating a payment when not authorized.
'''
@patch("../../controllers/payment_controller.db_create_payment", side_effect=fake_create_payment)
def test_create_payment_when_not_authorized() -> None:
    data: Payment = Payment(1, 12.5, "credit_card", "completed", datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"))
    response = client.post("/payments", headers=invalid_header, json=asdict(data))
    assert response.status_code == 401
    assert len(payments) == 0
    payments.clear()

'''
Test creating a payment when data is missing or invalid.
'''
@patch("../../controllers/payment_controller.db_create_payment", side_effect=fake_create_payment)
def test_create_payment_with_invalid_data() -> None:
    response = client.post("/payments", headers=valid_header, json={"amount": -10})
    assert response.status_code == 400
    assert len(payments) == 0
    payments.clear()

'''
Test refunding a payment when authorized.
'''
@patch("../../controllers/payment_controller.db_refund_payment", side_effect=fake_refund_payment)
def test_refund_payment_when_authorized() -> None:
    data: Payment = Payment(1, 12.5, "credit_card", "completed", datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"))
    response = client.post("/payments/refund", headers=valid_header, json=asdict(data))
    assert response.status_code == 201
    assert len(payments) == 1
    assert payments[0].amount < 0
    payments.clear()

'''
Test refunding a payment when missing amount field.
'''
@patch("../../controllers/payment_controller.db_refund_payment", side_effect=fake_refund_payment)
def test_refund_payment_missing_amount() -> None:
    response = client.post("/payments/refund", headers=valid_header, json={"method": "credit_card"})
    assert response.status_code == 400
    assert len(payments) == 0
    payments.clear()

'''
Test refunding a payment when not authorized.
'''
@patch("../../controllers/payment_controller.db_refund_payment", side_effect=fake_refund_payment)
def test_refund_payment_when_not_authorized() -> None:
    data: Payment = Payment(1, 12.5, "credit_card", "completed", datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"))
    response = client.post("/payments/refund", headers=invalid_header, json=asdict(data))
    assert response.status_code == 401
    assert len(payments) == 0
    payments.clear()