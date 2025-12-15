from fastapi import FastAPI
from api.app.routers import parking_lots, sessions, payments
from api.app.routers import profile, reservations, vehicles
from api.app.routers import admin_reservation_routes

app = FastAPI()

app.include_router(admin_reservation_routes.router)
app.include_router(reservations.router)
app.include_router(profile.router)
app.include_router(vehicles.router)
app.include_router(reservations.router)
app.include_router(sessions.router)
app.include_router(parking_lots.router)
app.include_router(payments.router)
