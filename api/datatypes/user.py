from pydantic import BaseModel
from typing import Optional
from datetime import date

class UserCreate(BaseModel):
    password: str
    email: str
    name: str
    phone: Optional[str] = None
    birth_year: Optional[date] = None

class User(UserCreate):
    id: int

class UserLogin(BaseModel):
    username: str
    password: str
