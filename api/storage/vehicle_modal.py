from api.datatypes.vehicles import Vehicles

#eventually the database queries / JSON write/read will be here.

class Vehicle_modal:
    def __init__(self):
        self.vehicle_list: list[Vehicles] = [
            {
                "id": 1,
                "user_id": 1,
                "license_plate": "76-KQQ-7",
                "make": "Peugeot",
                "model": "308",
                "color": "Brown",
                "year": 2024,
            },
            {
                "id": 2,
                "user_id": 2,
                "license_plate": "45-ASP-1",
                "make": "Opal",
                "model": "308",
                "color": "Blue",
                "year": 2022,
            },
            {
                "id": 3,
                "user_id": 1,
                "license_plate": "43-ZSO-4",
                "make": "Peugeot",
                "model": "Partner",
                "color": "Navy",
                "year": 2022,
            },
        ]
    
    #Return all vehicles
    def get_all_vehicles(self) -> list[Vehicles]:
        return self.vehicle_list
    
    #return all vehicles of user
    def get_all_user_vehicles(self, user_id) -> list[Vehicles]:
        return list(filter(lambda vehicle: vehicle["user_id"] == user_id, self.vehicle_list))
    
    #Return one vehicle
    def get_one_vehicle(self, vehicle_id) -> list[Vehicles]:
        return list(filter(lambda vehicle: vehicle["id"] == vehicle_id, self.vehicle_list))[0]
    
    #Creates vehicles
    def create_vehicle(self, vehicle_create) -> list[Vehicles]:
        vehicle_create["id"] = len(self.vehicle_list)
        self.vehicle_list.append(vehicle_create)
        return self.vehicle_list