import pytest
from datetime import timedelta, datetime
from api.auth_utils import (
    hash_password,
    create_access_token,
    revoke_token,
    is_token_revoked,
    require_role,
    require_lot_access,
    get_current_user,
    get_current_user_optional,
    JWTError,
)
from api.datatypes.user import User, UserRole
from fastapi import HTTPException
from unittest.mock import patch


def test_hash_password_returns_hash():
    hashed = hash_password("secret123")
    assert hashed != "secret123"

def test_create_access_token_contains_jwt():
    token = create_access_token({"sub": "superadmin"})
    assert isinstance(token, str)


def test_create_access_token_with_custom_expiry():
    token = create_access_token({"sub": "user"}, timedelta(minutes=1))
    assert isinstance(token, str)


def test_revoke_token_and_check():
    token = "token"
    revoke_token(token)
    assert is_token_revoked(token) is True


def test_is_token_revoked_false():
    assert is_token_revoked("fake-token") is False


def test_require_role_allows_correct_role():
    superadmin = User(
        id=1,
        username="superadmin",
        password="superadmin",
        email="super@admin.com",
        name="superadmin",
        role=UserRole.SUPERADMIN,
        created_at=datetime.now(),
        old_hash=False,
        phone=None,
        birth_year=None
    )

    rolecheck = require_role(UserRole.SUPERADMIN)
    assert rolecheck(superadmin) == superadmin


def test_require_role_blocks_wrong_role():
    user = User(
        id=1,
        username="user",
        password="user",
        email="user@user.com",
        name="user",
        role=UserRole.USER,
        created_at=datetime.now(),
        old_hash=False,
        phone=None,
        birth_year=None
    )

    rolecheck = require_role(UserRole.LOTADMIN)
    with pytest.raises(HTTPException) as exc_info:
        rolecheck(user)
    assert exc_info.value.status_code == 403


def test_superadmin_can_manage_any_lot():
    superadmin = User(
        id=1,
        username="superadmin",
        password="superadmin",
        email="super@admin.com",
        name="superadmin",
        role=UserRole.SUPERADMIN,
        created_at=datetime.now(),
        old_hash=False,
        phone=None,
        birth_year=None
    )

    wrapper = require_lot_access()
    assert wrapper(999, current_user=superadmin) == superadmin


@patch("api.auth_utils.user_model.get_parking_lots_for_admin",
       return_value=[10])
def test_admin_can_manage_assigned_lot(mock_get_lots):
    admin = User(
        id=2,
        username="admin",
        password="admin",
        email="admin@admin.com",
        name="admin",
        role=UserRole.LOTADMIN,
        created_at=datetime.now(),
        old_hash=False,
        phone=None,
        birth_year=None
    )

    wrapper = require_lot_access()
    assert wrapper(10, current_user=admin) == admin
    with pytest.raises(HTTPException) as exc:
        wrapper(99, current_user=admin)
    assert exc.value.status_code == 403


def test_user_cannot_manage_any_lot():
    user = User(
        id=3,
        username="user",
        password="user",
        email="user@user.com",
        name="user",
        role=UserRole.USER,
        created_at=datetime.now(),
        old_hash=False,
        phone=None,
        birth_year=None
    )

    wrapper = require_lot_access()
    with pytest.raises(HTTPException) as exc:
        wrapper(1, current_user=user)
    assert exc.value.status_code == 403


def _make_user(username: str) -> User:
    return User(
        id=1,
        username=username,
        password="pw",
        email=f"{username}@example.com",
        name=username,
        role=UserRole.USER,
        created_at=datetime.now(),
        old_hash=False,
        phone=None,
        birth_year=None,
    )


@patch("api.auth_utils.is_token_revoked", return_value=False)
@patch("api.auth_utils.jwt.decode", return_value={"sub": "alice"})
@patch("api.auth_utils.user_model.get_user_by_username",
       return_value=_make_user("alice"))
def test_get_current_user_valid(mock_get_user, mock_jwt_decode, mock_revoked):
    user = get_current_user("valid-token")
    assert user.username == "alice"


@patch("api.auth_utils.is_token_revoked", return_value=True)
def test_get_current_user_revoked(mock_revoked):
    with pytest.raises(HTTPException) as exc:
        get_current_user("revoked-token")
    assert exc.value.status_code == 401


@patch("api.auth_utils.jwt.decode", side_effect=JWTError("bad token"))
def test_get_current_user_invalid_token(mock_jwt_decode):
    with pytest.raises(HTTPException) as exc:
        get_current_user("invalid-token")
    assert exc.value.status_code == 401


@patch("api.auth_utils.is_token_revoked", return_value=False)
@patch("api.auth_utils.jwt.decode", return_value={})
def test_get_current_user_missing_sub(mock_jwt_decode, mock_revoked):
    with pytest.raises(HTTPException) as exc:
        get_current_user("no-sub-token")
    assert exc.value.status_code == 401


@patch("api.auth_utils.is_token_revoked", return_value=False)
@patch("api.auth_utils.jwt.decode", return_value={"sub": "unknown"})
@patch("api.auth_utils.user_model.get_user_by_username", return_value=None)
def test_get_current_user_user_not_found(mock_get_user, mock_jwt_decode,
                                         mock_revoked):
    with pytest.raises(HTTPException) as exc:
        get_current_user("unknown-user-token")
    assert exc.value.status_code == 401


def test_get_current_user_optional_handles_http_exception(monkeypatch):
    def mock_get_current_user(token):
        raise HTTPException(status_code=401, detail="Invalid token")

    import api.auth_utils as auth_utils
    monkeypatch.setattr(auth_utils, "get_current_user", mock_get_current_user)

    # Call get_current_user_optional with an invalid token
    result = get_current_user_optional(token="invalidtoken")
    assert result is None