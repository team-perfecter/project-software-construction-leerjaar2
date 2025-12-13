
from api.datatypes.vehicle import Vehicle, VehicleCreate
from psycopg2.extras import RealDictCursor
import psycopg2

class Vehicle_model:
    def __init__(self):
        self.connection = psycopg2.connect(
            host="db",
            port=5432,
            database="database",
            user="user",
            password="password",
        )

    #Return all vehicles
    def get_all_vehicles_of_user(self, user_id: int):
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM vehicles WHERE user_id = %s", (user_id,))
        return cursor.fetchall()
    
    #return all vehicles of user.
    def get_all_user_vehicles(self, user_id):
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM vehicles WHERE user_id = %s", (user_id,))
        return cursor.fetchall()
    
    # #Return a vehicle.
    def get_one_vehicle(self, id):
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, license_plate FROM vehicles")
        print("ALL VEHICLES (inside reservation):", cursor.fetchall(), flush=True)
        print("vehicle_id type:", type(id), "value:", id, flush=True)

        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM vehicles WHERE id = %s;
                       """, (id,))
        row = cursor.fetchone()
        print(row)
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    #Create a vehicle.
    def create_vehicle(self, vehicle: VehicleCreate):
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO vehicles (user_id, license_plate, make, model, color, year)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (vehicle.user_id, vehicle.license_plate, vehicle.make, vehicle.model, vehicle.color, vehicle.year))
        created = cursor.fetchone()
        self.connection.commit()
        return created is not None

    def update_vehicle(self, vehicle, vehicle_id):
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE vehicles
            SET license_plate=%s, make=%s, model=%s, color=%s, year=%s
            WHERE id=%s
        """, (vehicle["license_plate"], vehicle["make"], vehicle["model"], vehicle["color"], vehicle["year"], vehicle_id,))

    #Delete a vehicle.
    def delete_vehicle(self, vehicle_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM vehicles WHERE id=%s", (vehicle_id,))

    def get_all_Reservations_history_vehicles(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT *
            FROM reservations
            INNER JOIN vehicles
                ON reservations.vehicle_id = vehicles.vehicle_id
            INNER JOIN parking_lots p
                ON reservations.parking_lot_id = parkinglots.parking_lot_id
            WHERE reservations.user_id = %s
        """, (user_id,))