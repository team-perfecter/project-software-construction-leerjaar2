from api.auth_utils import *
from dataclasses import dataclass
from datetime import date

from fastapi import FastAPI

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
    return {"message": "user created succesfully"}

@app.get("/login")
async def login(data: LoginData):
    user = next((u for u in user_list if u.username == data.username), None)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/get_user/{user_id}")
async def get_user(user_id: int):
    return {"username: " + user_list[user_id].username, "password: " + user_list[user_id].password}

@app.get("/logout")
async def logout():
    revoke_token(token)


    
