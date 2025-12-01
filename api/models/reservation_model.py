import psycopg2
from api.datatypes.reservation import ReservationCreate

class ReservationModel:
    def __init__(self):
        self.connection = psycopg2.connect(
            host="db",
            port=5432,
            database="database",
            user="user",
            password="password",
        )

    def create_reservation(self, r: ReservationCreate):
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO reservations (user_id, vehicle_id, parking_lot_id, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (r.user_id, r.vehicle_id, r.parking_lot_id, r.start_time, r.end_time))
        new_id = cursor.fetchone()[0]
        self.connection.commit()
        return new_id

    def delete_reservation(self, reservation_id: int) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM reservations WHERE id = %s RETURNING id;", (reservation_id,))
        deleted = cursor.fetchone()
        self.connection.commit()
        return deleted is not None
