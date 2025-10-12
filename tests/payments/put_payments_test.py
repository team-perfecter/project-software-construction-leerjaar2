from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
import jwt
from unittest.mock import patch
from fastapi.testclient import TestClient
from ../../app import app

'''
when the PUT /payments/{transaction_id} endpoint is called, a user must provide a transaction ID and the data to update.
the API will check if the payment exists, and return 404 if not.
the API will then validate the data (amount > 0, valid status).
finally, the API updates the payment.
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
    payments.append(Payment(
        transaction_id,
        data.get("user_id", 0),
        data.get("amount", 0.0),
        data.get("method", "unknown"),
        data.get("status", "pending"),
        data.get("processed_by", "system"),
        datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    ))

def reset_payments() -> None:
    payments.clear()
    payments.append(Payment(
        "txn123", 1, 12.5, "credit_card", "completed", "alice", datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    ))

def create_test_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=30)
    return jwt.encode({"sub": username, "exp": expire}, "SECRET_KEY", algorithm="HS256")

token = create_test_token("alice")
valid_header = {"Authorization": f"Bearer {token}"}
invalid_header = {"Authorization": "Bearer invalid"}

'''
Test successfully updating a payment
'''
@patch("../../controllers/payment_controller.db_update_payment", side_effect=fake_put_payment)
def test_successfully_update_payment() -> None:
    reset_payments()
    payment_count_before = len(payments)
    assert payments[0].amount == 12.5

    data = {"amount": 15.0, "status": "completed", "processed_by": "alice"}
    response = client.put("/payments/txn123", headers=valid_header, json=data)

    assert response.status_code == 200
    assert len(payments) == payment_count_before
    assert payments[0].amount == 15.0
    reset_payments()

'''
Test updating a payment when not authorized
'''
@patch("../../controllers/payment_controller.db_update_payment", side_effect=fake_put_payment)
def test_update_payment_not_authorized() -> None:
    reset_payments()
    payment_count_before = len(payments)
    data = {"amount": 20.0, "status": "completed", "processed_by": "bob"}
    response = client.put("/payments/txn123", headers=invalid_header, json=data)

    assert response.status_code == 401
    assert len(payments) == payment_count_before
    assert payments[0].amount == 12.5
    reset_payments()

'''
Test updating a payment with incomplete data
'''
@patch("../../controllers/payment_controller.db_update_payment", side_effect=fake_put_payment)
def test_update_payment_incomplete_data() -> None:
    reset_payments()
    payment_count_before = len(payments)
    data = {"status": "completed"}
    response = client.put("/payments/txn123", headers=valid_header, json=data)

    assert response.status_code == 400
    assert len(payments) == payment_count_before
    assert payments[0].amount == 12.5
    reset_payments()

'''
Test updating a payment that does not exist
'''
@patch("../../controllers/payment_controller.db_update_payment", side_effect=fake_put_payment)
def test_update_payment_not_found() -> None:
    reset_payments()
    payment_count_before = len(payments)
    data = {"amount": 15.0, "status": "completed", "processed_by": "alice"}
    response = client.put("/payments/txn999", headers=valid_header, json=data)

    assert response.status_code == 404
    assert len(payments) == payment_count_before
    reset_payments()

'''
Test updating a payment with invalid data
'''
@patch("../../controllers/payment_controller.db_update_payment", side_effect=fake_put_payment)
def test_update_payment_invalid_data() -> None:
    reset_payments()
    payment_count_before = len(payments)
    data = {"amount": -50, "status": "completed", "processed_by": "alice"}
    response = client.put("/payments/txn123", headers=valid_header, json=data)

    assert response.status_code == 400
    assert len(payments) == payment_count_before
    assert payments[0].amount == 12.5
    reset_payments()
