import os
from fastapi import FastAPI
import api.logging_config # Needs to be imported for logging to be configured.
from api.app.routers import admin_reservation_routes, parking_lots, payments, profile, reservations, sessions, vehicles
from api.data_converter import DataConverter


if os.getenv("MIGRATE_JSON", "false").lower() == "true":
    data_converter: DataConverter = DataConverter()
    data_converter.convert()


app = FastAPI()

app.include_router(admin_reservation_routes.router)
app.include_router(reservations.router)
app.include_router(profile.router)
app.include_router(vehicles.router)
app.include_router(reservations.router)
app.include_router(sessions.router)
app.include_router(parking_lots.router)
app.include_router(payments.router)
