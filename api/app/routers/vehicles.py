from api.auth_utils import get_current_user
from api.datatypes.user import User
from fastapi import FastAPI, HTTPException, Body, Depends, APIRouter
from api.storage.profile_storage import Profile_storage
from api.models.vehicle_model import Vehicle_model
from api.datatypes.vehicle import Vehicle
import logging
from starlette.responses import JSONResponse

router = APIRouter(tags=["vehicles"])

#Models:
vehicle_model: Vehicle_model = Vehicle_model()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)






#Get:

#Get all vehicles from logged in user or get all vehicles if loggedin is ADMIN. (User and Admin)
@router.get("/vehicles")
async def vehicles():
    #Get all vehicles if you are Admin or get all your owned vehicles if you are user.
    vehicles = vehicle_model.get_all_vehicles() if get_current_user().role == "ADMIN" else vehicle_model.get_all_user_vehicles(get_current_user().id)
    return "No vehicles found" if vehicles == [] else vehicles

#Get one vehicle of an user. (User and Admin)
@router.get("/vehicles/{vehicle_id}")
async def vehicles(vehicle_id: int):
    #Get user vehicle.
    vehicle = vehicle_model.get_one_vehicle(vehicle_id)

    #Shows one vehicle if you are ADMIN or if it is the vehicle of the loggedin user.
    if get_current_user().role == "ADMIN" or get_current_user().id == vehicle["user_id"]:
        return vehicle
    else:
        return "Something went wrong."

#Get vehicles of an user. (Admin)
@router.get("/vehicles/user/{user_id}")
async def vehicles_user(user_id: int):
    #Get user vehicles.
    if get_current_user().role == "ADMIN":
        vehicles_user = vehicle_model.get_all_user_vehicles(user_id)
        return "Vehicles not found." if vehicles_user == [] else vehicles_user
    else:
        return "You are not autorized to this."



#Post:

#Create a vehicle for an user. (user)
@router.post("/vehicles/create")
async def vehicle_create(vehicle: dict = Body(...)):
    #Create vehicle.
    updated_list = vehicle_model.create_vehicle(vehicle)
    return updated_list



#Put:

#Update a vehicle for an user.
@router.put("/vehicles/update/{vehicle_id}")
async def vehicle_update(vehicle: dict = Body(...)):
    print("update vehicle of a user.")



#delete:

#delete a vehicle for an user.
@router.delete("vehicles/delete/{vehicle_id}")
async def vehicle_delete(vehicle_id: int, current_user: User = Depends(get_current_user)):
    user_id: int = current_user.id

    vehicle: Vehicle | None = vehicle_model.get_one_vehicle(vehicle_id)

    if vehicle == None:
        logging.warning("A user with the ID of %i tried to delete a vehicle with the ID of %i, but the vehicle could not be found.", user_id, vehicle_id)
        raise HTTPException(status_code=404, detail={"error": "vehicle not found"})
    
    if vehicle.user_id != user_id:
        logging.warning("A user with the ID of %i tried to delete a vehicle with the ID of %i, but the vehicle does not belong to the user.", user_id, vehicle_id)
        raise HTTPException(status_code=401, detail={"error": "Not authoized to delete this vehicle"})
    
    vehicle_model.delete_vehicle(vehicle.id)
    logging.info("A user with the ID of %i succesfully deleted a vehicle with the ID of %i.", user_id, vehicle_id)
    return JSONResponse(content={"message": "Vehicle succesfully deleted"}, status_code=201)

