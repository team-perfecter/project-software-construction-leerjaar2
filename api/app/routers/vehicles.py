from api.auth_utils import get_current_user, require_role
from api.datatypes.user import User
from fastapi import HTTPException, Body, Depends, APIRouter
from api.models.vehicle_model import Vehicle_model
from api.models.user_model import UserModel
from api.datatypes.vehicle import Vehicle, VehicleCreate
from api.datatypes.user import UserRole
from starlette.responses import JSONResponse
import psycopg2

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["vehicles"])


#Models:
vehicle_model: Vehicle_model = Vehicle_model()
user_model: UserModel = UserModel()

#Get:

#Get all vehicles from logged in user or get all vehicles if loggedin is ADMIN. (User and Admin)
@router.get("/vehicles")
async def vehicles(user: User = Depends(get_current_user)):
    logger.info("User %i is trying to retrieve their vehicles", user.id)
    #Get all vehicles if you are Admin or get all your owned vehicles if you are user.
    vehicles = vehicle_model.get_all_vehicles_of_user(user.id)
    if vehicles == []:
        logger.warning("No vehicles found for user %i", user.id)
        return JSONResponse(content={"message": "Vehicles not found"}, status_code=404)
    else:
        logger.info("%i vehicles found for user %i", len(vehicles), user.id)
        return vehicles


# Get one vehicle of an user. (Admin and up only)
@router.get("/vehicles/{vehicle_id}")
async def vehicles(
    vehicle_id: int,
    user: User = require_role(UserRole.LOTADMIN, UserRole.SUPERADMIN),
):
    logger.info("An admin tried to retrieve information about vehicle %i", vehicle_id)
    # Get user vehicle
    vehicle = vehicle_model.get_one_vehicle(vehicle_id)

    # Return 404 if vehicle does not exist
    if not vehicle:
        logger.warning("No vehicle found with the id %i", vehicle_id)
        raise HTTPException(status_code=404, detail="vehicle not found")
    else:
        # Shows one vehicle if you are ADMIN or SUPERADMIN
        logger.info("Vehicle %i found", vehicle_id)
        return vehicle


# Get vehicles of an user. (Admin)
@router.get("/vehicles/user/{user_id}")
async def vehicles_user(
    user_id: int,
    user: User = Depends(require_role(UserRole.LOTADMIN, UserRole.SUPERADMIN)),
):
    logger.info("An admin tried to retrieve all vehicles of user %i", user_id)
    # Check if user exists
    existing_user = user_model.get_user_by_id(user_id)
    if not existing_user:
        logger.warning("User %i not found", user_id)
        raise HTTPException(status_code=404, detail="user not found")
    
    # Get user vehicles
    vehicles_user = vehicle_model.get_all_user_vehicles(user_id)

    # Return 404 if no vehicles are found
    if not vehicles_user:
        logger.warning("No vehicles found for user %i", user_id)
        raise HTTPException(status_code=404, detail="vehicles not found")
    else:
        logger.info("%i vehicles found for user %i", len(vehicles_user), user_id)
        return vehicles_user

#Post:

#Create a vehicle for an user. (user)
@router.post("/vehicles/create")
async def vehicle_create(vehicle: VehicleCreate, user: User = Depends(get_current_user)):
    logger.info("User %i tried to create a new vehicle", user.id)
    #Create vehicle.
    vehicle = VehicleCreate(
        user_id=user.id,
        license_plate=vehicle.license_plate,
        make=vehicle.make,
        model=vehicle.model,
        color=vehicle.color,
        year=vehicle.year,
    )
    created = vehicle_model.create_vehicle(vehicle)
    if not created:
        logger.error("User %i could not create a new vehicle", user.id)
        raise HTTPException(status_code=500, detail="Failed to create vehicle")
    else:
        logger.info("User %i successfully created a new vehicle", user.id)
        return JSONResponse(content={"message": "Vehicle successfully created."}, status_code=201)

#Put:

#Update a vehicle for an user.
@router.put("/vehicles/update/{vehicle_id}")
async def vehicle_update(vehicle_id: int, vehicle: dict = Body(...), user: User = Depends(get_current_user)):
    #CHeck if vehicle exist.
    logger.info("User %i tried to update vehicle %i", user.id, vehicle_id)
    vehicle_check = vehicle_model.get_one_vehicle(vehicle_id)
    if vehicle_check == None:
        logger.warning("Vehicle %i not found", vehicle_id)
        raise HTTPException(detail={"message": "This vehicle doesn't exist."}, status_code=404)

    # Update vehicle
    if vehicle_check["user_id"] == user.id:
        vehicle_model.update_vehicle(vehicle, vehicle_id)
        logger.info("User %i successfully updated vehicle %i", user.id, vehicle_id)
        return JSONResponse(content={"message": "Vehicle succesfully updated"}, status_code=200)
    else:
        logger.warning("Vehicle %i does not belong to user %i. The vehicle was not updated", vehicle_id, user.id)
        raise HTTPException(detail={"message": "Something went wrong."}, status_code=403)

#delete:

#delete a vehicle for an user.
@router.delete("/vehicles/delete/{vehicle_id}")
async def vehicle_delete(vehicle_id: int, user: User = Depends(get_current_user)):
    logger.info("User %i tried to delete vehicle %i", user.id, vehicle_id)
    vehicle: Vehicle | None = vehicle_model.get_one_vehicle(vehicle_id)

    if vehicle is None:
        logging.warning(
            "A user with the ID of %i tried to delete a vehicle with the ID of %i, but the vehicle could not be found.",
            user.id, vehicle_id
        )
        raise HTTPException(status_code=404, detail={"error": "vehicle not found"})

    if vehicle["user_id"] != user.id:
        logging.warning(
            "A user with the ID of %i tried to delete a vehicle with the ID of %i, but the vehicle does not belong to the user.",
            user.id, vehicle_id
        )
        raise HTTPException(status_code=403, detail={"error": "Not authorized to delete this vehicle"})

    try:
        vehicle_model.delete_vehicle(vehicle_id)
        logging.info(
            "A user with the ID of %i successfully deleted a vehicle with the ID of %i.",
            user.id, vehicle_id
        )
    except psycopg2.errors.ForeignKeyViolation:
        logging.warning(
            "User %i tried to delete vehicle %i, but it is still referenced by active sessions.",
            user.id, vehicle_id
        )
        raise HTTPException(
            status_code=409,
            detail={"error": "Cannot delete vehicle: it is still referenced by active sessions."}
        )
    except Exception as e:
        logging.error(
            "An error occurred while deleting vehicle %i for user %i: %s",
            vehicle_id, user.id, str(e)
        )
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "message": str(e)}
        )

    return JSONResponse(content={"message": "Vehicle successfully deleted"}, status_code=200)
