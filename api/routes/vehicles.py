from dataclasses import dataclass

from fastapi import FastAPI, HTTPException

app = FastAPI()

@dataclass
class User:
    id: int
    username: str
    password: str
    name: str
    email: str
    phone: str
    role: str


user_list: list[User] = [
    {
        "id": 1,
        "username": "cindy.leenders42",
        "password": "6b37d1ec969838d29cb611deaff50a6b",
        "name": "Cindy Leenders",
        "email": "cindyleenders@upcmail.nl",
        "phone": "+310792215694",
        "role": "USER",
    },
    {
        "id": 2,
        "username": "gijsdegraaf",
        "password": "1b1f4e666f54b55ccd2c701ec3435dba",
        "name": "Gijs de Graaf",
        "email": "gijsdegraaf@hotmail.com",
        "phone": "+310698086312",
        "role": "ADMIN",
    },
    {
        "id": 3,
        "username": "iris.dekker70",
        "password": "bf7ea48e511957eccb06a832ba6ae6c9",
        "name": "Iris Dekker",
        "email": "iris.dekker70@yahoo.com",
        "phone": "+310207093519",
        "role": "USER",
    },
]

@dataclass
class Vehicles:
    id: int
    user_id: int
    license_plate: str
    make: str
    model: str
    color: str
    year: int


vehicle_list: list[Vehicles] = [
    {"id": 1, "user_id": 1, "license_plate": "76-KQQ-7", "make": "Peugeot", "model": "308", "color": "Brown", "year": 2024,},
    {"id": 2, "user_id": 2, "license_plate": "45-ASP-1", "make": "Opal", "model": "308", "color": "Blue", "year": 2022,},
    {"id": 3, "user_id": 1, "license_plate": "43-ZSO-4", "make": "Peugeot", "model": "Partner", "color": "Navy", "year": 2022,},
]


#Get:

temp_login_id = 2
#Get all vehicles from logged in user or get all vehicles if loggedin is ADMIN. (User and Admin)
@app.get("/vehicles")
async def vehicles():
    #Temperary login.
    auth = list(filter(lambda user: user["id"] == temp_login_id, user_list))[0]

    #Get all vehicles for Admin. Get All your owned vehicles for user.
    vehicles = vehicle_list if auth["role"] == "ADMIN" else list(filter(lambda vehicle: vehicle["user_id"] == auth["id"], vehicle_list))
    return "No vehicles found" if vehicles == [] else vehicles

#Get one vehicle of an user. (User and Admin)
@app.get("/vehicles/{vehicle_id}")
async def vehicles(vehicle_id: int):
    #Temperary login.
    auth = list(filter(lambda user: user["id"] == temp_login_id, user_list))[0]

    #Get user vehicle.
    vehicle = list(filter(lambda vehicle: vehicle["id"] == vehicle_id, vehicle_list))[0]

    #Shows the vehicle if you are ADMIN or if it is your vehicle.
    if auth["role"] == "ADMIN" or auth["role"] == "USER" and auth["id"] == vehicle["user_id"]:
        return vehicle
    else:
        return "Something went wrong."



#Get vehicles of an user. (Admin)
@app.get("/vehicles/user/{user_id}")
async def vehicles_user(user_id: int):
    vehicles_user = list(filter(lambda vehicle: vehicle["user_id"] == user_id, vehicle_list))
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