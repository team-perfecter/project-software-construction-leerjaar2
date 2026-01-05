import psycopg2

from api.datatypes.reservation import ReservationCreate, Reservation


#eventually the database queries / JSON write/read will be here.

class ReservationModel:
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
        return cursor.fetchone()

    def create_reservation(self, reservation: ReservationCreate) -> None:
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO reservations (vehicle_id, user_id, parking_lot_id, start_time, end_time, status, cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """, (
            reservation.vehicle_id, 
            reservation.user_id, 
            reservation.parking_lot_id, 
            reservation.start_time, 
            reservation.end_time, 
            reservation.status, 
            reservation.cost))
        self.connection.commit()
        return cursor.fetchone()[0]

    def get_reservation_by_vehicle(self, vehicle_id: int) -> list[Reservation]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM reservations WHERE vehicle_id = %s", (vehicle_id,))
        return cursor.fetchall()

    def delete_reservation(self, reservation_id: int) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM reservations WHERE id = %s RETURNING id;", (reservation_id,))
        deleted = cursor.fetchone()
        self.connection.commit()
        return deleted is not None
