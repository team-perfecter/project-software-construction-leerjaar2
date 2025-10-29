from api.datatypes.vehicles import Vehicles

#eventually the database queries / JSON write/read will be here.

class vehicle_model:
    def __init__(self):
        self.vehicle_list: list[Vehicles] = [
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
    
    def get_all_vehicles(self) -> list[Vehicles]:
        print("it works")
        return self.vehicle_list