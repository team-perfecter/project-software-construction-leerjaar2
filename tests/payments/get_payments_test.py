from unittest.mock import patch
from datetime import datetime, timedelta
import json
import jwt
import pytest
from fastapi.testclient import TestClient
from ../../app import app

'''
payments will be in a seperate class. the input of this class will be the authorization token of the user.
each endpoint will check if the token is valid. if not valid, return 401
the validity of a token is checked in the get_user(token: str = Depends(oauth2_scheme)) function.
get_payment(pid: int) returns the payment with the given payment id. this happens with the function db_get_payment(id: int)
get_payments_for_user(uid: int) returns all payments for the given user id. this happens with the function db_get_payments_for_user(id: int)
get_payment returns the followinig:
{"payment": db_get_payment(id: int)}
'''

client = TestClient(app)

'''
A function that creates a new authorization token so a user can be verified
'''
def create_test_token(username: str):
    expire = datetime.now() + timedelta(minutes=30)
    token = jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return token

token = create_test_token("alice")
valid_headers = {"Authorization": f"Bearer {token}"}
invalid_header = {"Authorization": "Bearer invalid"}

'''
Fake data used for mocking database responses
'''
def get_fake_payment(pid: int):
    return [{
        "id": "1",
        "user_id": "1",
        "amount": 12.5,
        "method": "credit_card",
        "status": "completed",
        "created_at": "2025-12-01T11:00:00Z"
    },
    {
        "id": "2",
        "user_id": "2",
        "amount": 8.7,
        "method": "paypal",
        "status": "completed",
        "created_at": "2025-12-02T17:30:00Z"
    }][pid]

'''
Fake data used for mocking database responses for all payments of a user
'''
def get_fake_payments_for_user(uid: int):
    payments = [
        {"id": "1", "user_id": "1", "amount": 12.5, "method": "credit_card", "status": "completed"},
        {"id": "2", "user_id": "2", "amount": 8.7, "method": "paypal", "status": "completed"}
    ]
    return [p for p in payments if p["user_id"] == str(uid)]


'''
Test if a payment is properly received.
'''
def test_get_payment_when_authorized():
    response = client.get("/payments/", headers=valid_headers)
    with patch("db_get_payment", side_effect=get_fake_payment):
        res = get_payment(0)
        assert res["id"] == get_fake_payment
        assert response.status_code == 200

'''
Test what will happen when a payment does not exist.
'''
def test_get_empty_payment():
    response = client.get("/payments", headers=valid_headers)
    with patch("db_get_payment", side_effect=get_fake_payment):
        res = get_payment(2)
        assert res["id"] == None
        assert response.status_code == 404

'''
Test what will happen when a user tries to get a payment when not authorized
'''
def test_get_payment_not_authorized():
    response = client.get("/payments", headers=invalid_header)
    with patch("db_get_payment", side_effect=get_fake_payment):
        res = get_payment(0)
        assert res["id"] == None
        assert response.status_code == 401


'''
Test getting all payments for a specific user when authorized
'''
def test_get_payments_for_user_when_authorized():
    response = client.get("/payments/1", headers=valid_headers)
    with patch("db_get_payments_for_user", side_effect=get_fake_payments_for_user):
        res = get_payments_for_user(1)
        assert res[0]["user_id"] == "1"
        assert response.status_code == 200

'''
Test getting payments for a user that does not exist
'''
def test_get_payments_for_user_not_found():
    response = client.get("/payments/3", headers=valid_headers)
    with patch("db_get_payments_for_user", side_effect=get_fake_payments_for_user):
        res = get_payments_for_user(3)
        assert res == []
        assert response.status_code == 404

'''
Test what will happen when trying to get a specific user's payments while not authorized
'''
def test_get_payments_for_user_not_authorized():
    response = client.get("/payments/1", headers=invalid_header)
    with patch("db_get_payments_for_user", side_effect=get_fake_payments_for_user):
        res = get_payments_for_user(1)
        assert res == []
        assert response.status_code == 401
