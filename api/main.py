from fastapi import FastAPI
from api.app.routers import parking_lot, sessions, payments, profile, reservations, vehicles
import os
from api.data_converter import DataConverter


if os.getenv("MIGRATE_JSON", "false").lower() == "true":
    data_converter: DataConverter = DataConverter()
    data_converter.convert()


app = FastAPI()

app.include_router(profile.router)
app.include_router(vehicles.router)
app.include_router(reservations.router)
app.include_router(sessions.router)
app.include_router(parking_lot.router)
app.include_router(payments.router)