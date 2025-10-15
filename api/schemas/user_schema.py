from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import date

class UserCreate(BaseModel):
    username: constr(strip_whitespace=True, min_length=3)
    password: constr(min_length=6)
    name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    birth_year: Optional[date]

class UserOut(BaseModel):
    id: int
    username: str
    name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    birth_year: Optional[date]

    class Config:
        orm_mode = True
