from dataclasses import dataclass
from fastapi import APIRouter, HTTPException, status, FastAPI
from database.model.vehicle_model import Vehicle_model
from api.storage.session_storage import Session_storage

router = APIRouter()

session_storage: Session_storage = Session_storage()
vehicle_model: Vehicle_model = Vehicle_model()

#Get all vehicles from logged in user or get all vehicles if loggedin is ADMIN. (User and Admin)
@router.get("/vehicles")
async def vehicles():
    #Get all vehicles for Admin. Get All your owned vehicles for user.
    vehicles = vehicle_model.get_all_vehicles() if auth["role"] == "ADMIN" else vehicle_model.get_all_user_vehicles(auth["id"])
    return "No vehicles found" if vehicles == [] else vehicles

#Get one vehicle of an user. (User and Admin)
@router.get("/vehicles/{vehicle_id}")
async def vehicles(vehicle_id: int):
    #Get user vehicle.
    vehicle_model.get_all_user_vehicles(vehicle_id)

    #Shows one vehicle if you are ADMIN or if it is the vehicle of the loggedin user.
    if auth["role"] == "ADMIN" or auth["role"] == "USER" and auth["id"] == vehicle["user_id"]:
        return vehicle
    else:
        return "Something went wrong."

#Get vehicles of an user. (Admin)
@router.get("/vehicles/user/{user_id}")
async def vehicles_user(user_id: int):
    vehicles_user = list(filter(lambda vehicle: vehicle["user_id"] == user_id, vehicle_list))
    return "Vehicles not found" if vehicles_user == [] else vehicles_user



#Post:

#Create a vehicle for an user.
@router.post("vehicles/create")
async def vehicle_create():
    print("create vehicle of a user.")



#Put:

#Update a vehicle for an user.
@router.put("vehicles/update/{vehicle_id}")
async def vehicle_update(vehicle_id):
    print("update vehicle of a user.")



#delete:

#delete a vehicle for an user.
@router.delete("vehicles/delete/{vehicle_id}")
async def vehicle_update(vehicle_id):
    print("delete vehicle of a user.")


@router.post("/vehicles/{vehicle_id}/session/start")
async def start_vehicle_session(vehicle_id: int):
    """Start een parkeersessie voor dit voertuig."""
    vehicle = vehicle_storage.get_vehicle_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    if auth["role"] != "ADMIN" and vehicle.user_id != auth["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        session = session_storage.start_session(vehicle_id, auth["id"], parking_lot_id=1)
        return {"message": "Session started successfully", "session": session}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/vehicles/{vehicle_id}/session/stop")
async def stop_vehicle_session(vehicle_id: int):
    """Stop de actieve parkeersessie van dit voertuig."""
    try:
        session = session_storage.stop_session(vehicle_id)
        return {"message": "Session stopped successfully", "session": session}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sessions")
async def get_all_sessions():
    """Bekijk alle sessies (debug/test)."""
    return session_storage.get_all_sessions()