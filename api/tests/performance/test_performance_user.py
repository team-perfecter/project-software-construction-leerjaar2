import pytest
from fastapi.testclient import TestClient
from api.main import app
from unittest.mock import patch
from api.datatypes.user import User, UserRole
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def mock_user_lookup():
    """Mock database lookup to isolate auth performance"""
    def fake_get_user(username: str) -> User | None:
        if username == "testuser":
            return User(
                id=1,
                username="testuser",
                password="5f4dcc3b5aa765d61d8327deb882cf99",  # MD5 hash of "password"
                email="test@example.com",
                name="Test User",
                role=UserRole.USER,
                created_at=datetime.now(),
                is_new_password=False,
                phone=None,
                birth_year=None
            )
        return None
    
    with patch("api.app.routers.profile.user_model.get_user_by_username", side_effect=fake_get_user):
        yield

@pytest.mark.benchmark(group="auth")
def test_login_success_performance(benchmark, mock_user_lookup):
    """Benchmark: Successful login with valid credentials"""
    payload = {"username": "testuser", "password": "password"}
    
    result = benchmark(
        client.post,
        "/login",
        json=payload
    )
    
    assert result.status_code == 200
    assert "access_token" in result.json()