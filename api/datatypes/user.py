from click import DateTime
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    LOTADMIN = "lotadmin"
    PAYMENTADMIN = "paymentadmin"
    SUPERADMIN = "superadmin"

class Register(BaseModel):
    username: str
    password: str
    email: str
    name: str
    phone: Optional[str] = None
    birth_year: Optional[int] = None

class User(Register):
    id: int
    created_at: datetime
    role: UserRole
    old_hash: bool
    active: bool

class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    name: str
    phone: Optional[str] = None
    birth_year: Optional[int] = None
    role: UserRole
    old_hash: Optional[bool] = False

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    birth_year: Optional[int] = None