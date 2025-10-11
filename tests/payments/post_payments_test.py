from unittest.mock import patch
from datetime import datetime, timedelta
import json
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
    expire = datetime.utcnow() + timedelta(minutes=30)
    token = jwt.encode({"sub": username, "exp": expire}, "SECRET_KEY", algorithm="HS256")
    return token

token = create_test_token("alice")
valid_headers = {"Authorization": f"Bearer {token}"}
invalid_headers = {"Authorization": "Bearer invalid"}

'''
Fake payment data used for mocking database responses
'''
def get_fake_payment_data():
    return {
        "user_id": "1",
        "amount": 12.5,
        "method": "credit_card",
        "status": "completed",
        "created_at": datetime.now().strftime("%d-%m-%Y %H:%I:%s")
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
        "created_at": datetime.now().strftime("%d-%m-%Y %H:%I:%s"),
        "completed": False,
        "hash": "hash123"
    }

'''
Test creating a payment when authorized
'''
def test_post_payment_when_authorized():
    response = client.post("/payments", headers=valid_headers, json=get_fake_payment_data())
    with patch("db_create_payment", return_value=get_fake_payment_data()):
        res = create_payment(get_fake_payment_data())
        assert res["amount"] == 12.5
        assert response.status_code == 201

'''
Test creating a payment with missing or invalid data
'''
def test_post_payment_invalid_data():
    response = client.post("/payments", headers=valid_headers, json={})
    with patch("db_create_payment", return_value=None):
        res = create_payment({})
        assert res is None
        assert response.status_code == 400

'''
Test creating a payment when not authorized
'''
def test_post_payment_not_authorized():
    response = client.post("/payments", headers=invalid_headers, json=get_fake_payment_data())
    with patch("db_create_payment", return_value=get_fake_payment_data()):
        res = create_payment(get_fake_payment_data())
        assert res is None
        assert response.status_code == 401

'''
Test refunding a payment (creates negative payment) when authorized
'''
def test_post_refund_payment_when_authorized():
    refund_data = {"amount": 12.5, "processed_by": "alice"}
    response = client.post("/payments/refund", headers=valid_headers, json=refund_data)
    with patch("db_refund_payment", side_effect=get_fake_refund):
        res = refund_payment(refund_data)
        assert res["amount"] < 0
        assert res["processed_by"] == "alice"
        assert response.status_code == 201

'''
Test refunding a payment when missing amount field
'''
def test_post_refund_payment_missing_amount():
    refund_data = {"processed_by": "alice"}
    response = client.post("/payments/refund", headers=valid_headers, json=refund_data)
    with patch("db_refund_payment", side_effect=get_fake_refund):
        res = refund_payment(refund_data)
        assert res["amount"] == 0 or res is None
        assert response.status_code == 400

'''
Test refunding a payment when not authorized
'''
def test_post_refund_payment_not_authorized():
    refund_data = {"amount": 12.5, "processed_by": "alice"}
    response = client.post("/payments/refund", headers=invalid_headers, json=refund_data)
    with patch("db_refund_payment", side_effect=get_fake_refund):
        res = refund_payment(refund_data)
        assert res is None
        assert response.status_code == 401
