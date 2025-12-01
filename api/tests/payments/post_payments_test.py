from fastapi.testclient import TestClient
from api.main import app
from api.auth_utils import create_access_token

client = TestClient(app)

def test_create_payment_with_superadmin():
    token = create_access_token({"sub": "superadmin"})
    headers = {"Authorization": f"Bearer {token}"}

    fake_payment = {
        "user_id": 1,
        "amount": 200,
        "method": "paypal"
    }

    response = client.post("/payments", json=fake_payment, headers=headers)
    
    assert response.status_code == 201
    assert response.json() == {"message": "Payment created successfully"}
D