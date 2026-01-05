from starlette.responses import JSONResponse
from api.datatypes.user import User, UserCreate, UserLogin, UserUpdate, UserRole, Register
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
async def register(user: Register):
    logging.info("A user it trying to create a new profile with the name %s", user.name)
    username_check = user_model.get_user_by_username(user.username)
    if username_check is not None:
        logging.warning("Profile not created. username is already taken")
        raise HTTPException(status_code=409, detail="Name already taken")
    # New users should have their passwords hashed with argon2
    hashed_password = hash_string(user.password)
    user.password = hashed_password
    user_model.create_user(user)
    logging.info("A user has created a new profile with the name: %s", user.name)

    return JSONResponse(content={"message": "User created successfully"}, status_code=201)


@router.post("/login")
async def login(data: UserLogin):
    logging.info("User %s is trying to login", data.username)
    user: User = user_model.get_user_by_username(data.username)
    if user is None:
        logging.info("Login failed, username not found: %s", data.username)
        raise HTTPException(status_code=404, detail="Username not found")
    if not verify_password(data.password, user.password):
        logging.info("Login failed, incorrect password for user: %s", data.username)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # updates password to use argon 2 when md5 is still used
    # if not user.is_new_password:
    #     hashed_password = hash_string(data.password, True)
    #     user_model.update_password(user.id, hashed_password)

    access_token = create_access_token({"sub": user.username})
    logging.info("User '%s' logged in successfully", user.username)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/get_user/{user_id}")
async def get_user(user_id: int, current_user: User = Depends(require_role(UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.PAYMENTADMIN))):
    logging.info("Admin %i is trying to access the information of user %i", current_user.id, user_id)
    user: User = user_model.get_user_by_id(user_id)
    if user is None:
        logging.warning("User %i could not be found", user_id)
        return JSONResponse(status_code=404, content={"message": "User not found"})
    return JSONResponse(status_code=200, content={"username: " + user.username, "password: " + user.password}) 


@router.get("/users")
async def admin_get_all_users(current_user: User = Depends(require_role(UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.PAYMENTADMIN))):
    logging.info("Admin %i tried to receive data of all users", current_user.id)
    users = user_model.get_all_users()
    return JSONResponse(status_code=200, content={"users": users})


@router.get("/profile", response_model=User)
async def get_me(user: User = Depends(get_current_user)):
    logging.info("User %i tried to receive information about their profile", user.id)
    if not user:
        logging.warning("User was not found")
        raise HTTPException(status_code=404, detail="User not found")
    else:
        logging.info("User %i received information about their profile", user.id)
        return JSONResponse(status_code=200, content={"information": user})


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme), user: User = Depends(get_current_user)):
    logging.info("User %i is trying to log out", user.id)
    if user:
        revoke_token(token)
        logging.info("User %i has logged out", user.id)
    else:
        return JSONResponse(status_code=401, content={"message": "User not logged in"})


@router.put("/update_profile")
async def update_me(update_data: UserUpdate, current_user: User = Depends(get_current_user)):
    logging.info("User %i is trying to update their profile", current_user.id)
    if not update_data:
        logging.warning("User %i did not provide update information of their profile", current_user.id)
        raise HTTPException(status_code=400, detail="No fields to update")
    update_fields = update_data.dict(exclude_unset=True)
    user_model.update_user(current_user.id, update_fields)
    logging.info("User %i successfully updated %s of their profile", current_user.id, update_fields)
    return JSONResponse(status_code=201, content={"message": "Profile updated successfully"})


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, current_user = require_role(UserRole.SUPERADMIN)):
    logging.info("A superadmin tried to delete the profile of user %i", user_id)
    user = user_model.get_user_by_id(user_id)
    if not user:
        logging.warning("Failed to delete user. User %i does not exist", user_id)
        raise HTTPException(status_code=404, detail="User not found")
    deleted = user_model.delete_user(user_id)
    if not deleted:
        logging.error("Failed to delete user")
        raise HTTPException(500, "Deletion was unsuccesful")
    logging.info("A superadmin successfully deleted user %i", user_id)
    return JSONResponse(status_code=200, content={"message": "User deleted successfully"})



@router.post("/create_user")
async def create_user(user: UserCreate, current_user: User = Depends(require_role(UserRole.SUPERADMIN))):
    logging.info("A superadmin tried to create a new user")
    username_check = user_model.get_user_by_username(user.username)
    if username_check is not None:
        logging.info(
            "A superadmin tried to create a profile, but the name was already created: %s", user.name)
        raise HTTPException(status_code=409, detail="Name already taken")
    hashed_password = hash_string(user.password)
    user.password = hashed_password
    user_model.create_user_with_role(user)
    logging.info(
        "A superadmin has created a new profile with the name: %s", user.name)

    return JSONResponse(content={"message": "User created successfully"}, status_code=201)


@router.post("/admin/{admin_id}/parking-lots/{lot_id}/assign")
async def assign_lot_to_admin(admin_id: int, lot_id: int, current_user: User = Depends(require_role(UserRole.SUPERADMIN))):
    logging.info("A superadmin gave admin %i access to parking lot %i", admin_id, lot_id)
    user_model.add_parking_lot_access(admin_id, lot_id)
    return JSONResponse(content={"message": "Parking lot access added"}, status_code=201)
