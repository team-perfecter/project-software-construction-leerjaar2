from fastapi import FastAPI
from api.app.routers import profile
from api.app.routers import parking_lot

app = FastAPI()

app.include_router(profile.router)
app.include_router(parking_lot.router)
