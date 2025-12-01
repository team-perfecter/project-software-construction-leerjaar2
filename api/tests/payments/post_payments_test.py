# api/tests/payments/post_payments_test.py
from fastapi.testclient import TestClient
from api.main import app
from api.auth_utils import create_access_token

client = TestClient(app)

def test_create_payment_with_superadmin():
    # Generate token for default SUPERADMIN in the DB
    token = create_access_token({"sub": "superadmin"})
    headers = {"Authorization": f"Bearer {token}"}

    fake_payment = {
        "user_id": 1,       # points to the SUPERADMIN itself
        "amount": 200,
        "method": "paypal"
    }

    response = client.post("/payments", json=fake_payment, headers=headers)
    
    assert response.status_code == 201
    assert response.json() == {"message": "Payment created successfully"}
