from fastapi import FastAPI
from api.app.routers import profile

app = FastAPI()

app.include_router(profile.router)
