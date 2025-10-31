from fastapi import FastAPI, HTTPException
from api.storage.profile_storage import Profile_storage
from api.storage.vehicle_modal import Vehicle_modal
from api.datatypes.vehicles import Vehicle
import logging
from starlette.responses import JSONResponse

app = FastAPI()

#Modals:
users_modal: Profile_storage = Profile_storage()
vehicle_modal: Vehicle_modal = Vehicle_modal()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


#Temperary login. (1 = user with cars), (2 = Admin), (3 = user with no cars)
temp_login_id = 2
auth = list(filter(lambda user: user["id"] == temp_login_id, users_modal.get_all_users()))[0]



#Get:

#Get all vehicles from logged in user or get all vehicles if loggedin is ADMIN. (User and Admin)
@app.get("/vehicles")
async def vehicles():
    #Get all vehicles for Admin. Get All your owned vehicles for user.
    vehicles = vehicle_modal.get_all_vehicles() if auth["role"] == "ADMIN" else vehicle_modal.get_all_user_vehicles(temp_login_id)
    return "No vehicles found" if vehicles == [] else vehicles

#Get one vehicle of an user. (User and Admin)
@app.get("/vehicles/{vehicle_id}")
async def vehicles(vehicle_id: int):
    #Get user vehicle.
    vehicle = vehicle_modal.get_one_vehicle(vehicle_id)

    #Shows one vehicle if you are ADMIN or if it is the vehicle of the loggedin user.
    if auth["role"] == "ADMIN" or auth["role"] == "USER" and auth["id"] == vehicle["user_id"]:
        return vehicle
    else:
        return "Something went wrong."

#Get vehicles of an user. (Admin)
@app.get("/vehicles/user/{user_id}")
async def vehicles_user(user_id: int):
    #Get user vehicles
    vehicles_user = vehicle_modal.get_all_user_vehicles(user_id)
    return "Vehicles not found" if vehicles_user == [] else vehicles_user



#Post:

#Create a vehicle for an user.
@app.post("vehicles/create")
async def vehicle_create():
    print("create vehicle of a user.")



#Put:

#Update a vehicle for an user.
@app.put("vehicles/update/{vehicle_id}")
async def vehicle_update(vehicle_id):
    print("update vehicle of a user.")



#delete:

#delete a vehicle for an user.
@app.delete("vehicles/delete/{vehicle_id}")
async def vehicle_update(vehicle_id: int):
    # check if the user is logged in
    user_id: int = 1

    vehicle: Vehicle | None = vehicle_modal.get_one_vehicle(vehicle_id)

    if vehicle == None:
        logging.warning("A user with the ID of %i tried to delete a vehicle with the ID of %i, but the vehicle could not be found.", user_id, vehicle_id)
        raise HTTPException(status_code=404, detail={"error": "vehicle not found"})
    
    if vehicle.user_id != user_id:
        logging.warning("A user with the ID of %i tried to delete a vehicle with the ID of %i, but the vehicle does not belong to the user.", user_id, vehicle_id)
        raise HTTPException(status_code=401, detail={"error": "Not authoized to delete this vehicle"})
    
    vehicle_modal.delete_vehicle(vehicle.id)
    logging.info("A user with the ID of %i succesfully deleted a vehicle with the ID of %i.", user_id, vehicle_id)
    return JSONResponse(content={"message": "Vehicle succesfully deleted"}, status_code=201)