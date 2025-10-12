from unittest.mock import patch
from datetime import datetime, timedelta
import jwt
import pytest
from fastapi.testclient import TestClient
from ../../app import app

'''
payments will be in a separate class. the input of this class will be the authorization token of the user.
each endpoint will check if the token is valid. if not valid, return 401
the validity of a token is checked in the get_user(token: str = Depends(oauth2_scheme)) function.
create_payment() creates a new payment with the given data. this happens with the function db_create_payment(data)
refund_payment() refunds a payment with the given data (creates a negative payment). this happens with the function db_refund_payment(data)
'''

client = TestClient(app)


'''
A function that creates a new authorization token so a user can be verified
'''
def create_test_token(username: str):
    expire = datetime.now() + timedelta(minutes=30)
    token = jwt.encode({"sub": username, "exp": expire}, "SECRET_KEY", algorithm="HS256")
    return token


token = create_test_token("alice")
valid_header: dict[str, str] = {"Authorization": f"Bearer {token}"}
invalid_header: dict[str, str] = {"Authorization": "Bearer invalid"}


'''
Fake payment data used for mocking database responses
'''
def get_fake_payment_data():
    return {
        "user_id": "1",
        "amount": 12.5,
        "method": "credit_card",
        "status": "completed",
        "created_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }


'''
Fake refund data used for mocking database responses
'''
def get_fake_refund(data):
    return {
        "transaction": data.get("transaction", "txn123"),
        "amount": -abs(data.get("amount", 0)),
        "coupled_to": data.get("coupled_to"),
        "processed_by": data.get("processed_by", "alice"),
        "created_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "completed": False,
        "hash": "hash123"
    }


payments: list[dict] = []


def fake_create_payment(data: dict) -> None:
    payments.append(data)


def fake_refund_payment(data: dict) -> dict:
    refund = get_fake_refund(data)
    payments.append(refund)
    return refund


'''
Test creating a payment when authorized
'''
@patch("../../controllers/payment_controller.db_create_payment", side_effect=fake_create_payment)
def test_post_payment_when_authorized(mock_create_payment) -> None:
    data = get_fake_payment_data()
    response = client.post("/payments", headers=valid_header, json=data)
    assert response.status_code == 201
    assert len(payments) == 1
    assert payments[0]["amount"] == 12.5
    payments.clear()


'''
Test creating a payment with missing or invalid data
'''
@patch("../../controllers/payment_controller.db_create_payment", side_effect=fake_create_payment)
def test_post_payment_invalid_data(mock_create_payment) -> None:
    response = client.post("/payments", headers=valid_header, json={})
    assert response.status_code == 400
    assert len(payments) == 0
    payments.clear()


'''
Test creating a payment when not authorized
'''
@patch("../../controllers/payment_controller.db_create_payment", side_effect=fake_create_payment)
def test_post_payment_not_authorized(mock_create_payment) -> None:
    data = get_fake_payment_data()
    response = client.post("/payments", headers=invalid_header, json=data)
    assert response.status_code == 401
    assert len(payments) == 0
    payments.clear()


'''
Test refunding a payment (creates negative payment) when authorized
'''
@patch("../../controllers/payment_controller.db_refund_payment", side_effect=fake_refund_payment)
def test_post_refund_payment_when_authorized(mock_refund_payment) -> None:
    data = {"amount": 12.5, "processed_by": "alice"}
    response = client.post("/payments/refund", headers=valid_header, json=data)
    assert response.status_code == 201
    assert len(payments) == 1
    assert payments[0]["amount"] < 0
    payments.clear()


'''
Test refunding a payment when missing amount field
'''
@patch("../../controllers/payment_controller.db_refund_payment", side_effect=fake_refund_payment)
def test_post_refund_payment_missing_amount(mock_refund_payment) -> None:
    data = {"processed_by": "alice"}
    response = client.post("/payments/refund", headers=valid_header, json=data)
    assert response.status_code == 400
    assert len(payments) == 0
    payments.clear()


'''
Test refunding a payment when not authorized
'''
@patch("../../controllers/payment_controller.db_refund_payment", side_effect=fake_refund_payment)
def test_post_refund_payment_not_authorized(mock_refund_payment) -> None:
    data = {"amount": 12.5, "processed_by": "alice"}
    response = client.post("/payments/refund", headers=invalid_header, json=data)
    assert response.status_code == 401
    assert len(payments) == 0
    payments.clear()
