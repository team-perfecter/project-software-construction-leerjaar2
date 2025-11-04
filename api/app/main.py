from fastapi import FastAPI
from api.app.routers import profile
from api.routes import vehicles

app = FastAPI()

app.include_router(profile.router)
app.include_router(vehicles.router)
