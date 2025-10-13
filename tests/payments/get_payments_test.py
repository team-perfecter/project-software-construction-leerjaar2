from dataclasses import dataclass
from datetime import datetime, timedelta
from unittest.mock import patch
from fastapi.testclient import TestClient
import jwt
from ../../app import app

'''
payments will be in a separate class. The input of this class will be the authorization token of the user.
Each endpoint checks if the token is valid; if not, return 401.
The validity of a token is checked in get_user(token: str = Depends(oauth2_scheme)).
get_payment(pid: int) returns the payment with the given payment id via db_get_payment(id: int)
get_payments_for_user(uid: int) returns all payments for the given user id via db_get_payments_for_user(id: int)
'''

client = TestClient(app)

def create_test_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=30)
    return jwt.encode({"sub": username, "exp": expire}, "SECRET_KEY", algorithm="HS256")

token: str = create_test_token("alice")
valid_headers = {"Authorization": f"Bearer {token}"}
invalid_header = {"Authorization": "Bearer invalid"}

@dataclass
class Payment:
    id: str
    user_id: str
    amount: float
    method: str
    status: str
    created_at: str

def get_fake_payment(pid: int) -> Payment:
    return [
        Payment("1", "1", 12.5, "credit_card", "completed", "2025-12-01T11:00:00Z"),
        Payment("2", "2", 8.7, "paypal", "completed", "2025-12-02T17:30:00Z")
    ][pid]

def get_fake_payments_for_user(uid: int):
    payments = [
        Payment("1", "1", 12.5, "credit_card", "completed", "2025-12-01T11:00:00Z"),
        Payment("2", "2", 8.7, "paypal", "completed", "2025-12-02T17:30:00Z")
    ]
    return [p for p in payments if p.user_id == str(uid)]

'''
Test if a payment is properly received.
'''
@patch("path.to.function.db_get_payment", side_effect=get_fake_payment)
def test_get_payment_when_authorized() -> None:
    response = client.get("/payments/0", headers=valid_headers)
    assert response.status_code == 200
    data = response.json().get("payment")
    assert data["id"] == "1"

'''
Test what will happen when a payment does not exist.
'''
@patch("path.to.function.db_get_payment", side_effect=get_fake_payment)
def test_get_empty_payment() -> None:
    response = client.get("/payments/2", headers=valid_headers)
    assert response.status_code == 404

'''
Test what will happen when a user tries to get a payment when not authorized
'''
@patch("path.to.function.db_get_payment", side_effect=get_fake_payment)
def test_get_payment_not_authorized() -> None:
    response = client.get("/payments/0", headers=invalid_header)
    assert response.status_code == 401

'''
Test getting all payments for a specific user when authorized
'''
@patch("path.to.function.db_get_payments_for_user", side_effect=get_fake_payments_for_user)
def test_get_payments_for_user_when_authorized() -> None:
    response = client.get("/payments/user/1", headers=valid_headers)
    assert response.status_code == 200
    data = response.json().get("payments")
    assert data[0]["user_id"] == "1"

'''
Test getting payments for a user that does not exist
'''
@patch("path.to.function.db_get_payments_for_user", side_effect=get_fake_payments_for_user)
def test_get_payments_for_user_not_found() -> None:
    response = client.get("/payments/user/3", headers=valid_headers)
    assert response.status_code == 404
    data = response.json().get("payments")
    assert data == []

'''
Test what will happen when trying to get a specific user's payments while not authorized
'''
@patch("path.to.function.db_get_payments_for_user", side_effect=get_fake_payments_for_user)
def test_get_payments_for_user_not_authorized() -> None:
    response = client.get("/payments/user/1", headers=invalid_header)
    assert response.status_code == 401
