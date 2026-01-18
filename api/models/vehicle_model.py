"""
This file contains all queries related to vehicles.
"""

from psycopg2.extras import RealDictCursor
from api.datatypes.vehicle import VehicleCreate
from api.models.connection import get_connection

class VehicleModel:
    """
    Handles all database operations related to vehicles.
    """

    def __init__(self):
        """
        Initialize a new VehicleModel instance and connect to the database.
        """
        self.connection = get_connection()

    def get_all_vehicles_of_user(self, user_id: int) -> list[dict]:
        """
        Retrieve all vehicles owned by a specific user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list[dict]: List of vehicle records as dictionaries.
        """
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM vehicles WHERE user_id = %s", (user_id,))
        return cursor.fetchall()

    def get_all_user_vehicles(self, user_id: int) -> list[dict]:
        """
        Alias for get_all_vehicles_of_user.
        Retrieves all vehicles for a user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list[dict]: List of vehicle records as dictionaries.
        """
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM vehicles WHERE user_id = %s", (user_id,))
        return cursor.fetchall()

    def get_one_vehicle(self, vehicle_id: int) -> dict | None:
        """
        Retrieve a single vehicle by its ID.

        Args:
            vehicle_id (int): The ID of the vehicle.

        Returns:
            dict | None: Vehicle data as a dictionary, or None if not found.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM vehicles WHERE id = %s;
        """, (vehicle_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    def create_vehicle(self, vehicle: VehicleCreate) -> bool:
        """
        Create a new vehicle record in the database.

        Args:
            vehicle (VehicleCreate): Data for the new vehicle.

        Returns:
            bool: True if the vehicle was successfully created, False otherwise.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO vehicles (user_id, license_plate, make, model, color, year)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (vehicle.user_id,
              vehicle.license_plate,
              vehicle.make,
              vehicle.model,
              vehicle.color,
              vehicle.year))
        created = cursor.fetchone()
        self.connection.commit()
        return created is not None

    def update_vehicle(self, vehicle: dict, vehicle_id: int) -> None:
        """
        Update an existing vehicle's details.

        Args:
            vehicle (dict): Vehicle data to update.
            vehicle_id (int): The ID of the vehicle to update.

        Returns:
            None
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE vehicles
            SET license_plate=%s, make=%s, model=%s, color=%s, year=%s
            WHERE id=%s
        """, (vehicle["license_plate"],
              vehicle["make"],
              vehicle["model"],
              vehicle["color"],
              vehicle["year"],
              vehicle_id,))
        self.connection.commit()

    def delete_vehicle(self, vehicle_id: int) -> None:
        """
        Delete a vehicle from the database by its ID.

        Args:
            vehicle_id (int): The ID of the vehicle to delete.

        Returns:
            None
        """
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM vehicles WHERE id=%s", (vehicle_id,))
        self.connection.commit()

    def get_all_reservations_history_vehicles(self, user_id: int) -> list[dict]:
        """
        Retrieve the reservation history for all vehicles of a specific user,
        including joined data from vehicles and parking lots.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list[dict]: List of reservation records with vehicle and parking lot info.
        """
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT *
            FROM reservations
            INNER JOIN vehicles
                ON reservations.vehicle_id = vehicles.vehicle_id
            INNER JOIN parking_lots p
                ON reservations.parking_lot_id = parkinglots.parking_lot_id
            WHERE reservations.user_id = %s
        """, (user_id,))
        return cursor.fetchall()
