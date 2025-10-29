from dataclasses import dataclass
from datetime import datetime, timedelta
from unittest.mock import patch
from fastapi.testclient import TestClient
import jwt
from ../../app import app

client = TestClient(app)

def create_test_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=30)
    return jwt.encode({"sub": username, "exp": expire}, "SECRET_KEY", algorithm="HS256")

token: str = create_test_token("alice")
valid_headers = {"Authorization": f"Bearer {token}"}
invalid_header = {"Authorization": "Bearer invalid"}

@dataclass
class Billing:
    id: str
    user_id: str
    amount_due: float
    due_date: str
    status: str
    created_at: str

def get_fake_billing(bid: int) -> Billing:
    return [
        Billing("1", "1", 50.0, "2025-12-10", "pending", "2025-12-01T11:00:00Z"),
        Billing("2", "2", 75.0, "2025-12-15", "paid", "2025-12-02T17:30:00Z")
    ][bid]

def get_fake_billings_for_user(uid: int):
    billings = [
        Billing("1", "1", 50.0, "2025-12-10", "pending", "2025-12-01T11:00:00Z"),
        Billing("2", "2", 75.0, "2025-12-15", "paid", "2025-12-02T17:30:00Z")
    ]
    return [b for b in billings if b.user_id == str(uid)]


@patch("path.to.function.db_get_billing", side_effect=get_fake_billing)
def test_get_billing_when_authorized() -> None:
    response = client.get("/billings/0", headers=valid_headers)
    data = response.json()
    assert response.status_code == 200
    assert data["billing"]["id"] == "1"


@patch("path.to.function.db_get_billing", side_effect=get_fake_billing)
def test_get_billing_not_found() -> None:
    response = client.get("/billings/2", headers=valid_headers)
    data = response.json()
    assert response.status_code == 404
    assert data.get("billing") is None


@patch("path.to.function.db_get_billing", side_effect=get_fake_billing)
def test_get_billing_not_authorized() -> None:
    response = client.get("/billings/0", headers=invalid_header)
    data = response.json()
    assert response.status_code == 401
    assert data.get("billing") is None


@patch("path.to.function.db_get_billings_for_user", side_effect=get_fake_billings_for_user)
def test_get_billings_for_user_when_authorized() -> None:
    response = client.get("/billings/user/1", headers=valid_headers)
    data = response.json()
    assert response.status_code == 200
    assert data["billings"][0]["user_id"] == "1"


@patch("path.to.function.db_get_billings_for_user", side_effect=get_fake_billings_for_user)
def test_get_billings_for_user_not_found() -> None:
    response = client.get("/billings/user/3", headers=valid_headers)
    data = response.json()
    assert response.status_code == 404
    assert data["billings"] == []


@patch("path.to.function.db_get_billings_for_user", side_effect=get_fake_billings_for_user)
def test_get_billings_for_user_not_authorized() -> None:
    response = client.get("/billings/user/1", headers=invalid_header)
    data = response.json()
    assert response.status_code == 401
    assert data["billings"] == []