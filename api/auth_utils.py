"""
This file contains functions related to authorization.
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from api.datatypes.user import User, UserRole
from api.models.user_model import UserModel
from api.utilities.hasher import hash_string

user_model: UserModel = UserModel()

SECRET_KEY = "super_secret_key"  # ⚠️ Gebruik een env var in productie
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["md5_crypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using the configured password context.

    Args:
        password (str): The plain-text password.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain-text password matches the hashed password.

    Args:
        plain_password (str): The plain-text password provided by the user.
        hashed_password (str): The hashed password stored in the database.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return hash_string(plain_password) == hashed_password


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token containing the given data.

    Args:
        data (dict): A dictionary of claims to include in the token payload.
        expires_delta (timedelta | None): Optional expiration time for the token.
            Defaults to ACCESS_TOKEN_EXPIRE_MINUTES if not provided.

    Returns:
        str: The encoded JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

revoked_tokens = set()


def revoke_token(token: str) -> None:
    """
    Revoke a JWT token by adding it to the blacklist.

    Args:
        token (str): The JWT token to revoke.
    """
    revoked_tokens.add(token)


def is_token_revoked(token: str) -> bool:
    """
    Check if a JWT token has been revoked.

    Args:
        token (str): The JWT token to check.

    Returns:
        bool: True if the token is revoked, False otherwise.
    """
    return token in revoked_tokens


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Retrieve the current user based on the provided JWT token.

    Checks token validity, expiration, and revocation status.

    Args:
        token (str): The JWT token provided in the Authorization header.

    Raises:
        HTTPException: If the token is revoked, invalid, expired, or user does not exist.

    Returns:
        User: The currently authenticated user.
    """
    if is_token_revoked(token):
        raise HTTPException(
            status_code=401, detail="Token has been revoked (user logged out)")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        user: User = user_model.get_user_by_username(username)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


def require_role(*allowed_roles):
    """
    Dependency generator to enforce that the current user has one of the allowed roles.

    Args:
        allowed_roles: A variable list of allowed UserRole values.

    Raises:
        HTTPException: If the user's role is not in the allowed roles.

    Returns:
        User: The current user if authorized.
    """
    def wrapper(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(403, "Not enough permissions")
        return current_user
    return wrapper


def user_can_manage_lot(user: User, lid: int) -> bool:
    """
    Determine whether a given user has access to manage a specific parking lot.

    Args:
        user (User): The user to check.
        lid (int): The ID of the parking lot.

    Returns:
        bool: True if the user can manage the lot, False otherwise.
    """
    if user.role == UserRole.SUPERADMIN:
        return True

    if user.role == UserRole.ADMIN:
        assigned_lots = user_model.get_parking_lots_for_admin(user.id)
        return lid in assigned_lots

    return False


def require_lot_access():
    """
    Dependency generator to enforce that the current user has access to a given parking lot.

    Raises:
        HTTPException: If the user does not have access to the parking lot.

    Returns:
        User: The current user if authorized.
    """
    def wrapper(
        lid: int,
        current_user: User = Depends(get_current_user)
    ):
        if not user_can_manage_lot(current_user, lid):
            raise HTTPException(403, "Not enough permissions for this lot")
        return current_user
    return wrapper
