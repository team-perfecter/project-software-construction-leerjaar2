from fastapi import FastAPI, HTTPException
from api.storage.profile_storage import Profile_storage
from api.storage.vehicle_modal import Vehicle_modal

app = FastAPI()

#Modals:
users_modal: Vehicle_modal = Profile_storage()
vehicle_modal: Vehicle_modal = Vehicle_modal()



#Get:

#Get all vehicles from logged in user or get all vehicles if loggedin is ADMIN. (User and Admin)
@app.get("/vehicles")
async def vehicles():
    print(vehicle_modal)
    #Get all vehicles for Admin. Get All your owned vehicles for user.
    vehicles = vehicle_modal.get_all_vehicles()
    return "No vehicles found" if vehicles == [] else vehicles

#Get one vehicle of an user. (User and Admin)
@app.get("/vehicles/{vehicle_id}")
async def vehicles(vehicle_id: int):
    #Get user vehicle.
    vehicle = list(filter(lambda vehicle: vehicle["id"] == vehicle_id, vehicle_modal.get_all_vehicles()))[0]

    #Shows one vehicle if you are ADMIN or if it is the vehicle of the loggedin user.
    if auth["role"] == "ADMIN" or auth["role"] == "USER" and auth["id"] == vehicle["user_id"]:
        return vehicle
    else:
        return "Something went wrong."

#Get vehicles of an user. (Admin)
@app.get("/vehicles/user/{user_id}")
async def vehicles_user(user_id: int):
    vehicles_user = list(filter(lambda vehicle: vehicle["user_id"] == user_id, vehicle_modal.get_all_vehicles()))
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
async def vehicle_update(vehicle_id):
    print("delete vehicle of a user.")