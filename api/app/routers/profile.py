from starlette.responses import JSONResponse
from api.datatypes.user import User, UserCreate
from api.storage.profile_storage import Profile_storage
from api.utilities.Hasher import hash_string
import logging
from fastapi import APIRouter, HTTPException

router = APIRouter(
    tags=["profile"]
)

storage: Profile_storage = Profile_storage()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


@router.post("/register")
async def register(user: UserCreate):

    missing_fields: list[str] = []
    if not user.username:
        missing_fields.append("username")
    if not user.password:
        missing_fields.append("password")
    if not user.email:
        missing_fields.append("email")

    if len(missing_fields) > 0:
        logging.info(
            "A user tried to create a profile, but did not fill in the following fields: %s", missing_fields)
        raise HTTPException(status_code=400, detail={
                            "missing_fields": missing_fields})

    username_check = storage.get_user_by_username(user.name)
    if username_check != None:
        logging.info(
            "A user tried to create a profile, but the name was already created: %s", user.name)
        raise HTTPException(status_code=409, detail="Name already taken")
    hashed_password = hash_string(user.password)
    user.password = hashed_password
    logging.info(
        "A user has created a new profile with the name: %s", user.name)

    return JSONResponse(content={"message": "User created successfully"}, status_code=201)


@router.get("/get_user/{user_id}")
async def get_user(user_id: int):
    user_list: list[User] = storage.user_list
    return {"username: " + user_list[user_id].username, "password: " + user_list[user_id].password}
