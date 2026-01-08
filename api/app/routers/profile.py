"""
This file contains all endpoints related to profile.
"""

import logging
from fastapi import Depends, APIRouter, HTTPException
from starlette.responses import JSONResponse
from api.datatypes.user import User, UserCreate, UserLogin, UserUpdate, UserRole, Register
from api.models.user_model import UserModel
from api.utilities.hasher import hash_string
from api.auth_utils import (
    verify_password,
    create_access_token,
    get_current_user,
    revoke_token,
    oauth2_scheme,
    require_role
    )

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
    """
    Register a new user profile.

    Args:
        user (Register): User registration data including username and password.

    Raises:
        HTTPException: 409 if the username is already taken.

    Returns:
        JSONResponse: Confirmation message that the user was created successfully.
    """

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
    """
    Log in a user and issue an access token.

    Args:
        data (UserLogin): The username and password of the user.

    Raises:
        HTTPException: 404 if the username does not exist.
        HTTPException: 401 if the password is incorrect.

    Returns:
        dict: Access token and token type for authentication.
    """

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
async def get_user(user_id: int,
                   _: User = Depends(require_role(UserRole.SUPERADMIN,
                                                    UserRole.ADMIN,
                                                    UserRole.PAYMENTADMIN))):
    """
    Retrieve details of a specific user by user ID. Admins only.

    Args:
        user_id (int): ID of the user to retrieve.
        _ (User): Injected admin user (via role requirement).

    Returns:
        dict or JSONResponse: User details if found; 404 JSONResponse if not found.
    """

    user: User = user_model.get_user_by_id(user_id)
    if user is None:
        return JSONResponse(status_code=404, content={"message": "User not found"})
    return {"username: " + user.username, "password: " + user.password}


@router.get("/users")
async def admin_get_all_users(_: User = Depends(require_role(UserRole.SUPERADMIN,
                                                            UserRole.ADMIN,
                                                            UserRole.PAYMENTADMIN))):
    """
    Retrieve all users in the system. Admins only.

    Args:
        _ (User): Injected admin user (via role requirement).

    Returns:
        list[User]: A list of all users.
    """
    users = user_model.get_all_users()
    return users


@router.get("/profile", response_model=User)
async def get_me(user: User = Depends(get_current_user)):
    """
    Retrieve the currently authenticated user's profile.

    Args:
        user (User): Injected current user via authentication token.

    Raises:
        HTTPException: 404 if the user does not exist.

    Returns:
        User: The current user's profile.
    """

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme), user: User = Depends(get_current_user)):
    """
    Log out the currently authenticated user by revoking their token.

    Args:
        token (str): The OAuth2 bearer token to revoke.
        user (User): The currently authenticated user.

    Returns:
        str: Confirmation message indicating logout status.
    """

    if user:
        revoke_token(token)
        return "logged out successfully"
    return "user not logged in"


@router.put("/update_profile")
async def update_me(update_data: UserUpdate, current_user: User = Depends(get_current_user)):
    """
    Update the profile of the currently authenticated user.

    Args:
        update_data (UserUpdate): Fields to update (only provided fields are applied).
        current_user (User): Currently authenticated user.

    Raises:
        HTTPException: 400 if no fields are provided to update.

    Returns:
        dict: Confirmation message that the profile was updated successfully.
    """

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    update_fields = update_data.dict(exclude_unset=True)
    user_model.update_user(current_user.id, update_fields)
    return {"message": "Profile updated"}


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, _ = require_role(UserRole.SUPERADMIN)):
    """
    Delete a user by ID. Only superadmins can perform this action.

    Args:
        user_id (int): The ID of the user to delete.
        _ (User): Injected superadmin user.

    Raises:
        HTTPException: 404 if the user does not exist.
        HTTPException: 500 if deletion fails.

    Returns:
        dict: Confirmation message indicating successful deletion.
    """

    user = user_model.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    deleted = user_model.delete_user(user_id)
    if not deleted:
        raise HTTPException(500, "Deletion was unsuccesful")
    return {"message": "User deleted successfully"}


@router.post("/create_user")
async def create_user(user: UserCreate, _: User = Depends(require_role(UserRole.SUPERADMIN))):
    """
    Create a new user with a specific role. Superadmins only.

    Args:
        user (UserCreate): User data including role and password.
        _ (User): Injected superadmin user.

    Raises:
        HTTPException: 409 if the username is already taken.

    Returns:
        JSONResponse: Confirmation message that the user was created successfully.
    """

    username_check = user_model.get_user_by_username(user.username)
    if username_check is not None:
        logging.info(
            "A user tried to create a profile, but the name was already created: %s", user.name)
        raise HTTPException(status_code=409, detail="Name already taken")
    hashed_password = hash_string(user.password)
    user.password = hashed_password
    user_model.create_user_with_role(user)
    logging.info(
        "A user has created a new profile with the name: %s", user.name)

    return JSONResponse(content={"message": "User created successfully"}, status_code=201)


@router.post("/admin/{admin_id}/parking-lots/{lot_id}/assign")
async def assign_lot_to_admin(admin_id: int,
                                lot_id: int,
                                _: User = Depends(require_role(UserRole.SUPERADMIN))):
    """
    Assign a parking lot to an admin user. Superadmins only.

    Args:
        admin_id (int): ID of the admin to assign the lot to.
        lot_id (int): ID of the parking lot to assign.
        _ (User): Injected superadmin user.

    Returns:
        dict: Confirmation message indicating that the parking lot access was added.
    """

    user_model.add_parking_lot_access(admin_id, lot_id)
    return {"message": "Parking lot access added"}
