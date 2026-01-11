import api.logging_config # Needs to be imported for logging to be configured.
from fastapi import FastAPI
from api.app.routers import parking_lots, sessions, payments
from api.app.routers import profile, reservations, vehicles

app = FastAPI()

app.include_router(reservations.router)
app.include_router(profile.router)
app.include_router(vehicles.router)
app.include_router(reservations.router)
app.include_router(sessions.router)
app.include_router(parking_lots.router)
app.include_router(payments.router)
