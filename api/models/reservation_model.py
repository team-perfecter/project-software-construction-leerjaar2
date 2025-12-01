import psycopg2
from api.datatypes.reservation import Reservation
from datetime import datetime

#eventually the database queries / JSON write/read will be here.

class Reservation_model:
    def __init__(self):
        self.connection = psycopg2.connect(
            host="db",
            port=5432,
            database="database",
            user="user",
            password="password",
        )

    def get_all_reservations(self) -> list[Reservation]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM reservations")
        return cursor.fetchall()
    
    def get_reservation_by_id(self, reservation_id) -> Reservation | None:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM reservations WHERE id = %s", (reservation_id,))
        row = cursor.fetchone()
        print(row)
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def create_reservation(self, reservation) -> None:
        print(reservation["parking_lot_id"], flush=True)
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO reservations (user_id, parking_lot_id, vehicle_id, start_time, end_time, status, created_at, cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (reservation["user_id"], reservation["parking_lot_id"], reservation["vehicle_id"], reservation["start_time"], reservation["end_time"], reservation["status"], datetime.now(), 1))
        self.connection.commit()
        return True

    def get_reservation_by_vehicle(self, vehicle_id: int) -> list[Reservation]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM reservations WHERE vehicle_id = %s", (vehicle_id,))
        return cursor.fetchall()

    #Delete a vehicle.
    def delete_reservation(self, reservation_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM reservations WHERE id=%s", (reservation_id,))
        self.connection.commit()
        return True