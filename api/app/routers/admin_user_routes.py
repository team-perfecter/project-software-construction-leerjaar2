from fastapi import APIRouter, Depends, HTTPException
from api.auth_utils import get_current_user, require_role
from api.models.user_model import UserModel
from api.datatypes.user import User, UserRole

router = APIRouter(tags=["admin-users"])
user_model = UserModel()


@router.get("/admin/users/{user_id}")
async def admin_get_user(user_id: int, current_user = require_role(UserRole.SUPERADMIN, UserRole.ADMIN)):
    user = user_model.get_user_by_id(user_id)
    if not user:
        raise HTTPException(404, "User not found")

    return user

@router.get("/admin/users")
async def admin_get_all_users(current_user = require_role("admin")):
    users = user_model.get_all_users()
    return users


@router.delete("/admin/users/{user_id}")
async def admin_delete_user(user_id: int, current_user = require_role(UserRole.SUPERADMIN, UserRole.ADMIN)):
    deleted = user_model.delete_user(user_id)
    if not deleted:
        raise HTTPException(404, "User not found or not deleted")

    return {"message": "User deleted successfully"}