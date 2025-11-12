from models.database_conn import database_conn
from api.datatypes.vehicle import Vehicle

#eventually the database queries / JSON write/read will be here.

class Vehicle_model:
    def __init__(self):
        self.cur = database_conn.cursor()

    #Return all vehicles
    def get_all_vehicles(self):
        self.cur.execute("SELECT * FROM vehicles")
        return self.cur.fetchall()
    
    #return all vehicles of user.
    def get_all_user_vehicles(self, user_id):
        self.cur.execute("SELECT * FROM vehicles WHERE user_id = %s", (user_id))
        return self.cur.fetchall()
    
    #Return a vehicle.
    def get_one_vehicle(self, vehicle_id):
        self.cur.execute("SELECT * FROM vehicles WHERE id = %s", (vehicle_id))
        return self.cur.fetchone()

    #Create a vehicle.
    def create_vehicle(self, user_id, vehicle):
        self.cur.execute("""
            INSERT INTO vehicles (user_id, license_plate, make, model, color, year)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, vehicle["license_plate"], vehicle["make"], vehicle["model"], vehicle["color"], vehicle["year"]))
        self.cur.fetchone()
        return self.get_all_user_vehicles(user_id)

    def update_vehicle(self, vehicle):
        self.cur.execute("""
            UPDATE vehicles
            SET license_plate=%s, make=%s, model=%s, color=%s, year=%s
            WHERE id=%s
        """, (vehicle["license_plate"], vehicle["make"], vehicle["model"], vehicle["color"], vehicle["year"], vehicle["id"]))
        self.cur.fetchone()

    #Delete a vehicle.
    def delete_vehicle(self, vehicle_id):
        self.cur.execute("DELETE FROM vehicles WHERE id=%s", (vehicle_id))
        self.cur.fetchone()
        