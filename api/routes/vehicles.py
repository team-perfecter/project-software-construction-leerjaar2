from dataclasses import dataclass

from fastapi import FastAPI

app = FastAPI()

@dataclass
class Vehicles:
    id: int
    user_id: int
    license_plate: str
    make: str
    model: str
    color: str
    year: int


user_list: list[Vehicles] = [
    {"id": 1, "user_id": 1, "license_plate": "76-KQQ-7", "make": "Peugeot", "model": "308", "color": "Brown", "year": 2024,},
    {"id": 2, "user_id": 2, "license_plate": "45-ASP-1", "make": "Opal", "model": "308", "color": "Blue", "year": 2022,},
    {"id": 3, "user_id": 1, "license_plate": "43-ZSO-4", "make": "Peugeot", "model": "Partner", "color": "Navy", "year": 2022,},
]


#Get:

#Get all vehicles from logged in user.
@app.get("/vehicles")
async def vehicles():
    print("Get all vehicles.")

#Get vehicles of an user.
@app.get("/vehicles/user/{user_id}")
async def vehicle_user(user_id):
    print("Get vehicle of a user.")



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