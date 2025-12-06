from starlette.responses import JSONResponse
from api.datatypes.user import User, UserCreate, UserLogin, UserUpdate, UserRole, AdminCreate
from api.models.user_model import UserModel
from api.utilities.Hasher import hash_string
import logging
from fastapi import Depends, APIRouter, HTTPException
from api.auth_utils import verify_password, create_access_token, get_current_user, revoke_token, oauth2_scheme, require_role

router = APIRouter(
    tags=["profile"]
)

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
    # New users should have their passwords hashed with argon2
    hashed_password = hash_string(user.password)
    user.password = hashed_password
    user_model.create_user(user)
    logging.info(
        "A user has created a new profile with the name: %s", user.name)

    return JSONResponse(content={"message": "User created successfully"}, status_code=201)


@router.post("/login")
async def login(data: UserLogin):
    user: User = user_model.get_user_by_username(data.username)
    if user is None:
        logging.info("Login failed — username not found: %s", data.username)
        raise HTTPException(status_code=404, detail="Username not found")
    if not verify_password(data.password, user.password):
        logging.info("Login failed — incorrect password for user: %s", data.username)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # updates password to use argon 2 when md5 is still used
    # if not user.is_new_password:
    #     hashed_password = hash_string(data.password, True)
    #     user_model.update_password(user.id, hashed_password)

    access_token = create_access_token({"sub": user.username})
    logging.info("User '%s' logged in successfully", user.username)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/get_user/{user_id}")
async def get_user(user_id: int):
    user: User = user_model.get_user_by_id(user_id)
    if user is None:
        return JSONResponse(status_code=404, content={"message": "User not found"})
    return {"username: " + user.username, "password: " + user.password}


@router.get("/profile", response_model=User)
async def get_me(user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme), user: User = Depends(get_current_user)):
    if user:
        revoke_token(token)
        return "logged out successfully"
    return "user not logged in"


@router.put("/update_profile")
async def update_me(update_data: UserUpdate, current_user: User = Depends(get_current_user)):
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    update_fields = update_data.dict(exclude_unset=True)
    user_model.update_user(current_user.id, update_fields)
    return {"message": "Profile updated"}

@router.post("/create_admin")
async def create_admin(user: AdminCreate, current_user: User = Depends(require_role(UserRole.SUPERADMIN))):
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
    user_model.create_admin(user)
    logging.info(
        "A user has created a new profile with the name: %s", user.name)

    return JSONResponse(content={"message": "User created successfully"}, status_code=201)

@router.post("/admin/{admin_id}/parking-lots/{lot_id}/assign")
async def assign_lot_to_admin(admin_id: int, lot_id: int, current_user: User = Depends(require_role(UserRole.SUPERADMIN))):
    user_model.add_parking_lot_access(admin_id, lot_id)
    return {"message": "Parking lot access added"}
