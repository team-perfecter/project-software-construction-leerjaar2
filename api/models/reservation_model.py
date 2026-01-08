"""
This file contains all queries related to reservations.
"""

from api.datatypes.reservation import ReservationCreate, Reservation
from api.models.connection import get_connection


class ReservationModel:
    """
    Handles all database operations for reservations.

    Attributes:
        connection (psycopg2.connection): PostgreSQL database connection.
    """

    def __init__(self):
        """
        Initialize a new ReservationModel instance and connect to the database.
        """
        self.connection = get_connection()

    def get_all_reservations(self) -> list[Reservation]:
        """
        Retrieve all reservations from the database.

        Returns:
            list[Reservation]: A list of all reservations.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM reservations")
        return cursor.fetchall()

    def get_reservation_by_id(self, reservation_id: int) -> Reservation | None:
        """
        Retrieve a reservation by its ID.

        Args:
            reservation_id (int): The ID of the reservation to retrieve.

        Returns:
            Reservation | None: The reservation if found, else None.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM reservations WHERE id = %s", (reservation_id,))
        return cursor.fetchone()

    def create_reservation(self, reservation: ReservationCreate):
        """
        Create a new reservation in the database.

        Args:
            reservation (ReservationCreate): The reservation data to insert.

        Returns:
            int: The newly created reservation.
        """
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
            reservation.cost
        ))
        self.connection.commit()
        return cursor.fetchone()[0]

    def get_reservation_by_vehicle(self, vehicle_id: int) -> list[Reservation]:
        """
        Retrieve all reservations associated with a specific vehicle.

        Args:
            vehicle_id (int): The ID of the vehicle.

        Returns:
            list[Reservation]: A list of reservations for the given vehicle.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM reservations WHERE vehicle_id = %s", (vehicle_id,))
        return cursor.fetchall()

    def delete_reservation(self, reservation_id: int) -> bool:
        """
        Delete a reservation by its ID.

        Args:
            reservation_id (int): The ID of the reservation to delete.

        Returns:
            bool: True if the reservation was deleted, False if it did not exist.
        """
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM reservations WHERE id = %s RETURNING id;", (reservation_id,))
        deleted = cursor.fetchone()
        self.connection.commit()
        return deleted is not None
