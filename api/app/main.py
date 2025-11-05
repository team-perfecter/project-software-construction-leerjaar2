from fastapi import FastAPI
from api.app.routers import profile, reservations, payments, vehicles

app = FastAPI()

app.include_router(profile.router)
app.include_router(vehicles.router)
app.include_router(reservations.router)

app.include_router(payments.router)