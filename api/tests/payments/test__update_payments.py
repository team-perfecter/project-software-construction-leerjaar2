from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

# payments/{payment_id}

def test_update_payment(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_payment = {
        "user_id": 1,
        "amount": 200,
        "method": "updatedmethod",
        "completed": False,
        "refund_requested": False
    }
    response = client.put("/payments/1", json=fake_payment, headers=headers)
    assert response.status_code == 200

    client, headers = client_with_token("superadmin")
    response = client.get("/payments/1", headers=headers)
    assert response.status_code == 200

    assert response.json()["method"] == "updatedmethod"