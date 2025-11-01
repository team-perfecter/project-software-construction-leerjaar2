from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from api.datatypes.user import User
from api.storage.profile_storage import Profile_storage
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

profile_storage: Profile_storage = Profile_storage()

# ===== CONFIG =====
SECRET_KEY = "super_secret_key"  # ⚠️ use environment variable in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ===== PASSWORD HASHING =====
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# ===== JWT CREATION =====
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ===== TOKEN VALIDATION =====
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user: User = profile_storage.get_user_by_username(username)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
