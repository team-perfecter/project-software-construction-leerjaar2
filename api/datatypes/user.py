from pydantic import BaseModel
from typing import Optional
from datetime import date

class UserCreate(BaseModel):
    username: str
    password: str
    name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    birth_year: Optional[date] = None

class User(UserCreate):
    id: int