import os
from fastapi import FastAPI
from api.app.routers import parking_lots, sessions, payments
from api.app.routers import profile, reservations, vehicles
from api.app.routers import discount_codes
from api.data_converter import DataConverter

if os.getenv("MIGRATE_JSON", "false").lower() == "true":
    data_converter: DataConverter = DataConverter()
    data_converter.convert()

app = FastAPI()

app.include_router(reservations.router)
app.include_router(profile.router)
app.include_router(vehicles.router)
app.include_router(reservations.router)
app.include_router(sessions.router)
app.include_router(parking_lots.router)
app.include_router(payments.router)
app.include_router(discount_codes.router)
