from fastapi import FastAPI
from api.app.routers import parking_lot, sessions, payments, profile, reservations, vehicles, admin_user_routes, admin_reservation_routes

app = FastAPI()

app.include_router(admin_user_routes.router)
app.include_router(admin_reservation_routes.router)
#app.include_router(reservations.router)
app.include_router(profile.router)
app.include_router(vehicles.router)
app.include_router(reservations.router)
app.include_router(sessions.router)
app.include_router(parking_lot.router)
app.include_router(payments.router)