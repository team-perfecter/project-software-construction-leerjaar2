from api.auth_utils import get_current_user, require_role
from api.datatypes.user import User
from fastapi import FastAPI, HTTPException, Body, Depends, APIRouter
from api.models.vehicle_model import Vehicle_model
from api.models.user_model import UserModel
from api.datatypes.vehicle import Vehicle, VehicleCreate
from api.datatypes.user import UserRole
import logging
from starlette.responses import JSONResponse

router = APIRouter(tags=["vehicles"])


#Models:
vehicle_model: Vehicle_model = Vehicle_model()
user_model: UserModel = UserModel()

#Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

#Get:

#Get all vehicles from logged in user or get all vehicles if loggedin is ADMIN. (User and Admin)
@router.get("/vehicles")
async def vehicles(user: User = Depends(get_current_user)):
    #Get all vehicles if you are Admin or get all your owned vehicles if you are user.
    vehicles = vehicle_model.get_all_vehicles_of_user(user.id)
    return JSONResponse(content={"message": "Vehicles not found"}, status_code=404) if vehicles == [] else vehicles


# Get one vehicle of an user. (Admin and up only)
@router.get("/vehicles/{vehicle_id}")
async def vehicles(
    vehicle_id: int,
    user: User = require_role(UserRole.ADMIN, UserRole.SUPERADMIN),
):
    # Get user vehicle
    vehicle = vehicle_model.get_one_vehicle(vehicle_id)

    # Return 404 if vehicle does not exist
    if not vehicle:
        raise HTTPException(status_code=404, detail="vehicle not found")

    # Shows one vehicle if you are ADMIN or SUPERADMIN
    logging.warning(vehicle)
    return vehicle


# Get vehicles of an user. (Admin)
@router.get("/vehicles/user/{user_id}")
async def vehicles_user(
    user_id: int,
    user: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPERADMIN)),
):
    
    # Check if user exists
    existing_user = user_model.get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="user not found")
    
    # Get user vehicles
    vehicles_user = vehicle_model.get_all_user_vehicles(user_id)

    # Return 404 if no vehicles are found
    if not vehicles_user:
        raise HTTPException(status_code=404, detail="vehicles not found")

    return vehicles_user

#Post:

#Create a vehicle for an user. (user)
@router.post("/vehicles/create")
async def vehicle_create(vehicle: VehicleCreate, user: User = Depends(get_current_user)):
    #Create vehicle.
    print(vehicle)
    vehicle = VehicleCreate(
        user_id=user.id,
        license_plate=vehicle.license_plate,
        make=vehicle.make,
        model=vehicle.model,
        color=vehicle.color,
        year=vehicle.year,
    )
    print(vehicle)
    created = vehicle_model.create_vehicle(vehicle)
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create vehicle")
    return JSONResponse(content={"message": "Vehicle successfully created."}, status_code=201)

#Put:

#Update a vehicle for an user.
@router.put("/vehicles/update/{vehicle_id}")
async def vehicle_update(vehicle_id: int, vehicle: dict = Body(...), user: User = Depends(get_current_user)):
    #CHeck if vehicle exist.
    vehicle_check = vehicle_model.get_one_vehicle(vehicle_id)
    if vehicle_check == None:
        raise HTTPException(detail={"message": "This vehicle doesn't exist."}, status_code=404)

    # Update vehicle
    if vehicle_check["user_id"] == user.id:
        vehicle_model.update_vehicle(vehicle, vehicle_id)
        return JSONResponse(content={"message": "Vehicle succesfully updated"}, status_code=200)
    else:
        raise HTTPException(detail={"message": "Something went wrong."}, status_code=500)

#delete:

#delete a vehicle for an user.
@router.delete("/vehicles/delete/{vehicle_id}")
async def vehicle_delete(vehicle_id: int, user: User = Depends(get_current_user)):
    vehicle: Vehicle | None = vehicle_model.get_one_vehicle(vehicle_id)

    if vehicle == None:
        logging.warning("A user with the ID of %i tried to delete a vehicle with the ID of %i, but the vehicle could not be found.", user.id, vehicle_id)
        raise HTTPException(status_code=404, detail={"error": "vehicle not found"})

    if vehicle["user_id"] != user.id:
        logging.warning("A user with the ID of %i tried to delete a vehicle with the ID of %i, but the vehicle does not belong to the user.", user.id, vehicle_id)
        raise HTTPException(status_code=403, detail={"error": "Not authoized to delete this vehicle"})
    
    vehicle_model.delete_vehicle(vehicle_id)
    logging.info("A user with the ID of %i succesfully deleted a vehicle with the ID of %i.", user.id, vehicle_id)
    return JSONResponse(content={"message": "Vehicle succesfully deleted"}, status_code=200)