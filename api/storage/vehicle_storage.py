from api.datatypes.vehicle import Vehicle
from dataclasses import dataclass
from typing import List, Optional

#eventually the database queries / JSON write/read will be here.

# Eventueel importeren vanuit jouw datatypes map:
# from api.datatypes.vehicle import Vehicle
# maar voor nu definieer ik hem hier zodat het werkt zonder extra bestand.

@dataclass
class Vehicle:
    id: int
    user_id: int
    license_plate: str
    make: str
    model: str
    color: str
    year: int


class Vehicle_storage:
    """In-memory opslag voor voertuigen (testversie, zonder database)."""

    def __init__(self):
        #Tijdelijke testdata
        self.vehicle_list: List[Vehicle] = [
            Vehicle(1, 1, "76-KQQ-7", "Peugeot", "308", "Brown", 2024),
            Vehicle(2, 2, "45-ASP-1", "Opel", "Corsa", "Blue", 2022),
            Vehicle(3, 1, "43-ZSO-4", "Peugeot", "Partner", "Navy", 2022),
        ]

    #Alle voertuigen ophalen
    def get_all_vehicles(self) -> List[Vehicle]:
        return self.vehicle_list

    #Één voertuig opzoeken via ID
    def get_vehicle_by_id(self, id: int) -> Optional[Vehicle]:
        for vehicle in self.vehicle_list:
            if vehicle.id == id:
                return vehicle
        return None

    #Alle voertuigen van een gebruiker ophalen
    def get_vehicles_by_user(self, user_id: int) -> List[Vehicle]:
        return [v for v in self.vehicle_list if v.user_id == user_id]

    #Nieuw voertuig toevoegen
    def post_vehicle(self, vehicle: Vehicle) -> Vehicle:
        # Genereer automatisch nieuw ID
        vehicle.id = len(self.vehicle_list) + 1
        self.vehicle_list.append(vehicle)
        return vehicle

    #Voertuig verwijderen
    def delete_vehicle(self, vehicle_id: int) -> bool:
        before_count = len(self.vehicle_list)
        self.vehicle_list = [v for v in self.vehicle_list if v.id != vehicle_id]
        return len(self.vehicle_list) < before_count
