from api.datatypes.vehicle import Vehicle

#eventually the database queries / JSON write/read will be here.

class Vehicle_storage:
    def __init__(self):
        self.vehicle_list: list[Vehicle] = []

    def get_all_vehicles(self) -> list[Vehicle]:
        return self.vehicle_list

    def get_vehicle_by_id(self, id: int) -> Vehicle | None:
        for vehicle in self.vehicle_list:
            if vehicle.id == id:
                return vehicle
        return None
    
    def post_vehicle(self, vehicle: Vehicle) -> None:
        self.vehicle_list.append(vehicle)