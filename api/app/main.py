from fastapi import FastAPI
from api.app.routers import profile, reservations

app = FastAPI()

app.include_router(profile.router)
app.include_router(reservations.router)
