import hashlib
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


user_list: list[User] = []

@app.post("/register")
async def register(user: User):
    hashed_password = hashlib.md5(user.password.encode()).hexdigest()
    user.password = hashed_password
    user_list.append(user)
    return {"message": "user created succesfully"}

@app.get("/get_user/{user_id}")
async def get_user(user_id: int):
    return {"username: " + user_list[user_id].username, "password: " + user_list[user_id].password}
