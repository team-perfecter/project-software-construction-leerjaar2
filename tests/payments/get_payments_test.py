from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from ../../app import app

'''
payments will be in a seperate class. the input of this class will be the authorization token of the user.
each endpoint will check if the token is valid. if not valid, return 401
the validity of a token is checked in the get_user(token: str = Depends(oauth2_scheme)) function.
get_payment(pid: int) returns the payment with the given payment id. this happens with the function db_get_payment(id; int)
get_payment returns the followinig:
{"payment": db_get_payment(id: int)}
'''

client = TestClient(app)

'''
A function that creates a new authorization token so a user can be verified
'''
def create_test_token(username: str):
    expire = datetime.utcnow() + timedelta(minutes=30)
    token = jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return token

token = create_test_token("alice")
valid_headers = {"Authorization": f"Bearer {token}"}
invalid_header = {"Authorization": "Bearer invalid"}

def get_fake_payment(pid: int): #geen idee of velden kloppen, ik kan de json niet openen
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
