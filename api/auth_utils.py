from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from api.datatypes.user import User
from fastapi import HTTPException, status, Depends
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from api.models.user_model import UserModel

user_model: UserModel = UserModel()

SECRET_KEY = "super_secret_key"  # ⚠️ Gebruik een env var in productie
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

revoked_tokens = set()


def revoke_token(token: str):
    """Voeg een token toe aan de blacklist wanneer er wordt uitgelogd."""
    revoked_tokens.add(token)


def is_token_revoked(token: str) -> bool:
    """Controleer of token is ingetrokken."""
    return token in revoked_tokens


def get_current_user(token: str = Depends(oauth2_scheme)):
    """Controleer of token geldig en niet ingetrokken is."""
    if is_token_revoked(token):
        raise HTTPException(
            status_code=401, detail="Token has been revoked (user logged out)")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Invalid token payload")
        user: User = user_model.get_user_by_username(username)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
