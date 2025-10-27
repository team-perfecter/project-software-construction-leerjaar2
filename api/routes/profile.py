from dataclasses import dataclass
from datetime import date
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, status, Depends
from api.auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    revoke_token,
    oauth2_scheme,
)

app = FastAPI()

@dataclass
class User:
    username: str
    password: str
    name: str
    email: str
    phone: str
    birth_year: date

class LoginData(BaseModel):
    username: str
    password: str

user_list: list[User] = []

@app.post("/register")
async def register(user: User):
    user.password = hash_password(user.password)
    user_list.append(user)
    return {"message": "User created successfully"}

@app.post("/login")
async def login(data: LoginData):
    user = next((u for u in user_list if u.username == data.username), None)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """Server-side logout: token ongeldig maken."""
    revoke_token(token)
    return {"message": "User logged out successfully"}
