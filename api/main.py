"""
Main file of the API.
"""
import os
import api.logging_config # Needs to be imported for logging to be configured.
from fastapi import FastAPI
from api.app.routers import (parking_lots,
                             sessions,
                             payments,
                             profile,
                             reservations,
                             vehicles,
                             discount_codes)
from api.data_converter import DataConverter
if os.getenv("MIGRATE_JSON", "false").lower() == "true":
    data_converter: DataConverter = DataConverter()
    data_converter.convert()

app = FastAPI()

app.include_router(reservations.router)
app.include_router(profile.router)
app.include_router(vehicles.router)
app.include_router(sessions.router)
app.include_router(parking_lots.router)
app.include_router(payments.router)
app.include_router(discount_codes.router)
