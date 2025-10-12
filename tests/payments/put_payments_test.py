from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from unittest.mock import patch
import jwt
import pytest
from fastapi.testclient import TestClient
from ../../app import app

'''
when the put /payments/{transaction_id} endpoint is called, a user must fill in 2 fields: a transaction id and the data that must be updated
the api will check if the payment exists, and return a 404 if it does not
the api will then check if the data the user has sent is valid (for example, amount > 0 and valid status)
lastly, the api will update the payment
'''

client = TestClient(app)

@dataclass
class Payment:
    transaction: str
    user_id: int
    amount: float
    method: str
    status: str
    processed_by: str
    created_at: str

payments: list[Payment] = []


def fake_put_payment(transaction_id: str, data: dict) -> None:
    for i in range(len(payments)):
        if payments[i].transaction == transaction_id:
            payments.pop(i)
            break
    payments.append(Payment(transaction_id, data.get("user_id", 0), data.get("amount", 0.0), data.get("method", "unknown"), data.get("status", "pending"), data.get("processed_by", "system"), datetime.now().strftime("%d-%m-%Y %H:%I:%S")))


def get_fake_payment(transaction_id: str) -> Payment | None:
    for pay in payments:
        if pay.transaction == transaction_id:
            return pay
    return None


def reset_payments() -> None:
    payments.clear()
    payments.append(Payment("txn123", 1, 12.5, "credit_card", "completed", "alice", datetime.now().strftime("%d-%m-%Y %H:%I:%S")))


def create_test_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=30)
    token = jwt.encode({"sub": username, "exp": expire}, "SECRET_KEY", algorithm="HS256")
    return token


token: str = create_test_token("alice")
valid_header: dict[str, str] = {"Authorization": f"Bearer {token}"}
invalid_header: dict[str, str] = {"Authorization": "Bearer invalid"}


'''
Test successfully updating a payment
'''
@patch("../../controllers/payment_controller.db_update_payment", side_effect=fake_put_payment)
def test_successfully_update_payment() -> None:
    reset_payments()
    payment_amount_before = len(payments)
    assert payments[0].amount == 12.5

    data: dict = {"amount": 15.0, "status": "completed", "processed_by": "alice"}
    response = client.put("/payments/txn123", headers=valid_header, json=data)

    assert response.status_code == 200
    assert len(payments) == payment_amount_before
    assert payments[0].amount == 15.0
    reset_payments()


'''
Test updating a payment when not authorized
'''
@patch("../../controllers/payment_controller.db_update_payment", side_effect=fake_put_payment)
def test_update_payment_not_authorized() -> None:
    reset_payments()
    payment_amount_before = len(payments)
    assert payments[0].amount == 12.5

    data: dict = {"amount": 20.0, "status": "completed", "processed_by": "bob"}
    response = client.put("/payments/txn123", headers=invalid_header, json=data)

    assert response.status_code == 401
    assert len(payments) == payment_amount_before
    assert payments[0].amount == 12.5
    reset_payments()


'''
Test updating a payment when not all data is filled in
'''
@patch("../../controllers/payment_controller.db_update_payment", side_effect=fake_put_payment)
def test_update_payment_incomplete_data() -> None:
    reset_payments()
    payment_amount_before = len(payments)
    assert payments[0].amount == 12.5

    data: dict = {"status": "completed"}
    response = client.put("/payments/txn123", headers=valid_header, json=data)

    assert response.status_code == 400
    assert len(payments) == payment_amount_before
    assert payments[0].amount == 12.5
    reset_payments()


'''
Test updating a payment that does not exist
'''
@patch("../../controllers/payment_controller.db_update_payment", side_effect=fake_put_payment)
def test_update_payment_not_found() -> None:
    reset_payments()
    payment_amount_before = len(payments)

    data: dict = {"amount": 15.0, "status": "completed", "processed_by": "alice"}
    response = client.put("/payments/txn999", headers=valid_header, json=data)

    assert response.status_code == 404
    assert len(payments) == payment_amount_before
    reset_payments()


'''
Test updating a payment with invalid data
'''
@patch("../../controllers/payment_controller.db_update_payment", side_effect=fake_put_payment)
def test_update_payment_invalid_data() -> None:
    reset_payments()
    payment_amount_before = len(payments)
    assert payments[0].amount == 12.5

    data: dict = {"amount": -50, "status": "completed", "processed_by": "alice"}
    response = client.put("/payments/txn123", headers=valid_header, json=data)

    assert response.status_code == 400
    assert len(payments) == payment_amount_before
    assert payments[0].amount == 12.5
    reset_payments()
