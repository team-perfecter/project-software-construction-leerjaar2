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
update_payment(transaction_id: str, data) updates the payment with the given transaction ID. this happens with the function db_update_payment(transaction_id, data)
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
Fake update data for mocking database responses
'''
def get_fake_update_data():
    return {
        "amount": 15.0,
        "status": "completed",
        "processed_by": "alice"
    }

'''
Fake updated payment response
'''
def get_fake_updated_payment(transaction_id, data):
    return {
        "transaction": transaction_id,
        "amount": data.get("amount", 12.5),
        "status": data.get("status", "completed"),
        "processed_by": data.get("processed_by", "alice"),
        "updated_at": datetime.now().strftime("%d-%m-%Y %H:%I:%s")
    }

'''
Test updating a payment successfully
'''
def test_put_payment_when_authorized():
    transaction_id = "txn123"
    response = client.put(f"/payments/{transaction_id}", headers=valid_headers, json=get_fake_update_data())
    with patch("db_update_payment", side_effect=get_fake_updated_payment):
        res = update_payment(transaction_id, get_fake_update_data())
        assert res["transaction"] == transaction_id
        assert res["amount"] == 15.0
        assert response.status_code == 200

'''
Test updating a payment with missing or invalid data
'''
def test_put_payment_invalid_data():
    transaction_id = "txn123"
    response = client.put(f"/payments/{transaction_id}", headers=valid_headers, json={})
    with patch("db_update_payment", side_effect=get_fake_updated_payment):
        res = update_payment(transaction_id, {})
        assert res is None
        assert response.status_code == 400

'''
Test updating a payment that does not exist
'''
def test_put_payment_not_found():
    transaction_id = "txn999"
    response = client.put(f"/payments/{transaction_id}", headers=valid_headers, json=get_fake_update_data())
    with patch("db_update_payment", side_effect=lambda tid, data: None):
        res = update_payment(transaction_id, get_fake_update_data())
        assert res is None
        assert response.status_code == 404

'''
Test updating a payment when not authorized
'''
def test_put_payment_not_authorized():
    transaction_id = "txn123"
    response = client.put(f"/payments/{transaction_id}", headers=invalid_headers, json=get_fake_update_data())
    with patch("db_update_payment", side_effect=get_fake_updated_payment):
        res = update_payment(transaction_id, get_fake_update_data())
        assert res is None
        assert response.status_code == 401
