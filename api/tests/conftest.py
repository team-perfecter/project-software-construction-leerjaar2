# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.datatypes.user import User, UserRole


# ---- Provide FastAPI TestClient ----
@pytest.fixture
def client():
    return TestClient(app)


# ---- Helper fixture to override require_role with any role ----
@pytest.fixture
def override_role():
    """
    Usage in test:
        client = override_role(UserRole.SUPERADMIN)
        client = override_role(UserRole.PAYMENTADMIN)
        client = override_role(UserRole.USER)
    """
    def _override(*roles):
        # Function that returns a fake user with the first role
        def fake_current_user():
            return User(
                id=1,
                username="test_user",
                password="fake",
                email="test@example.com",
                name="Test User",
                role=roles[0] if roles else UserRole.USER,
                created_at=None,
                is_new_password=False,
                phone=None,
                birth_year=None
            )

        # Override dependency in FastAPI
        from api.auth_utils import require_role
        app.dependency_overrides[require_role] = lambda *args: fake_current_user
        return TestClient(app)

    return _override
