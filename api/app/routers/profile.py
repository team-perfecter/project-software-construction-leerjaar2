from starlette.responses import JSONResponse
from api.datatypes.user import User, UserCreate, UserLogin
from api.models.user_model import UserModel
from api.storage.profile_storage import Profile_storage
from api.utilities.Hasher import hash_string
import logging
from fastapi import Depends, APIRouter, HTTPException
from api.auth_utils import verify_password, create_access_token, get_current_user

router = APIRouter(
    tags=["profile"]
)

storage: Profile_storage = Profile_storage()
user_model: UserModel = UserModel()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


@router.post("/register")
async def register(user: UserCreate):

    missing_fields: list[str] = []
    if not user.name:
        missing_fields.append("name")
    if not user.password:
        missing_fields.append("password")
    if not user.email:
        missing_fields.append("email")

    if len(missing_fields) > 0:
        logging.info(
            "A user tried to create a profile, but did not fill in the following fields: %s", missing_fields)
        raise HTTPException(status_code=400, detail={
                            "missing_fields": missing_fields})

    username_check = user_model.get_user_by_username(user.username)
    if username_check is not None:
        logging.info(
            "A user tried to create a profile, but the name was already created: %s", user.name)
        raise HTTPException(status_code=409, detail="Name already taken")
    hashed_password = hash_string(user.password)
    user.password = hashed_password
    user_model.create_user(user)
    logging.info(
        "A user has created a new profile with the name: %s", user.name)

    return JSONResponse(content={"message": "User created successfully"}, status_code=201)

@router.post("/login")
async def login(data: UserLogin):
    user = user_model.get_user_by_username(data.username)
    if user is None:
        logging.info("Login failed — username not found: %s", data.username)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(data.password, user.password):
        logging.info("Login failed — incorrect password for user: %s", data.username)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.name})
    logging.info("User '%s' logged in successfully", user.name)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/get_user/{user_id}")
async def get_user(user_id: int):
    user: User = user_model.get_user_by_id(user_id)
    if user is None:
        return JSONResponse(status_code=404, content={"message": "User not found"})
    return {"username: " + user.username, "password: " + user.password}

@router.get("/profile", response_model=User)
async def get_me(username: str = Depends(get_current_user)):
    user = user_model.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
