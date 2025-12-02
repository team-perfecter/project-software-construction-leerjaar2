import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.auth_utils import create_access_token

@pytest.fixture
def client():
    """Provides a FastAPI TestClient instance."""
    return TestClient(app)

@pytest.fixture
def client_with_token(client):
    """
    Returns a TestClient and headers with JWT token for a given role.
    
    Usage:
        client, headers = client_with_token("superadmin")
        client, headers = client_with_token("paymentadmin")
    """
    def _client_with_role(username: str):
        token = create_access_token({"sub": username})
        headers = {"Authorization": f"Bearer {token}"}
        return client, headers

    return _client_with_role
