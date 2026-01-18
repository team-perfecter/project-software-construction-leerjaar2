"""
this file contains all queries related to parking lots.
"""

from typing import List, Optional
from pydantic_core import ValidationError
from api.datatypes.parking_lot import ParkingLot, ParkingLotCreate, ParkingLotFilter
from api.datatypes.session import Session
from api.models.connection import get_connection

class ParkingLotModel:
    """
    This class contains all queries related to parking lots.
    """
    def __init__(self):
        self.connection = get_connection()

    # region get
    def get_all_parking_lots(self) -> List[ParkingLot]:
        """
        Returns a list of all parking lots
        @return: list of ParkingLot objects
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM parking_lots;")
        return self.map_to_parking_lot(cursor)

    def get_parking_lot_by_lid(self, lot_id: int) -> Optional[ParkingLot]:
        """
        return a specific parking lot based on the given id
        @param: lot_id
        @returns: ParkingLot object based on id
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM parking_lots WHERE id = %s;", (lot_id,))
        lots = self.map_to_parking_lot(cursor)
        return lots[0] if lots else None

    def get_all_sessions_by_lid(self, lot_id: int) -> List[Session]:
        """
        Returns all sessions based on a parking lot id
        @param: lot_id
        @return: list of Session objects
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sessions WHERE parking_lot_id = %s;", (lot_id,))
        return self.map_to_session(cursor)

    def get_session_by_lid_and_sid(
        self, lot_id: int, session_id: int
    ) -> Optional[Session]:
        """
        Gets a specific session inside a specific parking lot based on session id and parking lot id
        @param: lot_id
        @param: session_id
        @return: Session object
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM sessions WHERE parking_lot_id = %s AND id = %s;",
            (lot_id, session_id),
        )
        sessions = self.map_to_session(cursor)
        return sessions[0] if sessions else None

    @staticmethod
    def map_to_session(cursor) -> List[Session]:
        """
        Maps the cursor to a session object
        @param: cursor
        @return: session object
        """
        columns = [desc[0] for desc in cursor.description]
        sessions = []
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            try:
                session = Session.model_validate(row_dict)
                sessions.append(session)
            except ValidationError  as e:
                print("Failed to map row to Session:", row_dict, e)
        return sessions

    def find_parking_lots(
        self,
        filters: ParkingLotFilter
    ) -> List[ParkingLot]:
        """
        Finds parking lots based on data provided with this method.
        @param: lot_id
        @param: name
        @param: location
        @param: city
        @param: min_capacity
        @param: max_capacity
        @param: min_tariff
        @param: max_tariff
        @param: has_availability
        @return: list of ParkingLot objects
        """
        cursor = self.connection.cursor()

        query = "SELECT * FROM parking_lots WHERE 1=1"
        params = []

        if filters.lot_id is not None:
            query += " AND id = %s"
            params.append(filters.lot_id)

        if filters.name is not None:
            query += " AND name ILIKE %s"
            params.append(f"%{filters.name}%")

        if filters.location is not None:
            query += " AND location ILIKE %s"
            params.append(f"%{filters.location}%")

        if filters.city is not None:
            query += " AND SPLIT_PART(address, ' ', -1) ILIKE %s"
            params.append(f"%{filters.city}%")

        if filters.min_capacity is not None:
            query += " AND capacity >= %s"
            params.append(filters.min_capacity)

        if filters.max_capacity is not None:
            query += " AND capacity <= %s"
            params.append(filters.max_capacity)

        if filters.min_tariff is not None:
            query += " AND tariff >= %s"
            params.append(filters.min_tariff)

        if filters.max_tariff is not None:
            query += " AND tariff <= %s"
            params.append(filters.max_tariff)

        if filters.has_availability is not None and filters.has_availability:
            query += " AND (capacity - reserved) > 0"

        query += ";"

        cursor.execute(query, params)
        return self.map_to_parking_lot(cursor)

    # region post

    def create_parking_lot(self, lot: ParkingLot) -> None:
        """
        Creates a parking lot based on the data provided.
        @param: lot
        """
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO parking_lots 
            (name, 
            location, 
            address, 
            capacity, 
            reserved, 
            tariff, 
            daytariff, 
            created_at, 
            lat, 
            lng, 
            status, 
            closed_reason, 
            closed_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """,
            (
                lot.name,
                lot.location,
                lot.address,
                lot.capacity,
                lot.reserved,
                lot.tariff,
                lot.daytariff,
                lot.created_at,
                lot.lat,
                lot.lng,
                lot.status,
                lot.closed_reason,
                lot.closed_date,
            ),
        )
        self.connection.commit()

    # region update

    def update_parking_lot(self, lot_id: int, lot: ParkingLotCreate) -> bool:
        """
        Updates a parking lot based on the data provided.
        @param: lot_id
        @param: lot
        @return: True if update was successful
        """
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE parking_lots 
            SET name = %s, location = %s, address = %s, capacity = %s, 
                tariff = %s, daytariff = %s, lat = %s, lng = %s,
                status = %s, closed_reason = %s, closed_date = %s
            WHERE id = %s;
        """,
            (
                lot.name,
                lot.location,
                lot.address,
                lot.capacity,
                lot.tariff,
                lot.daytariff,
                lot.lat,
                lot.lng,
                lot.status,
                lot.closed_reason,
                lot.closed_date,
                lot_id,
            ),
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def update_parking_lot_reserved(self, lot_id: int, amount: int) -> bool:
        """
        Updates a parking lot based on the data provided.
        @param: lot_id
        @param: lot
        @return: True if update was successful
        """
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE parking_lots 
            SET reserved = %s
            WHERE id = %s;
        """,
            (
                amount,
                lot_id,
            ),
        )
        self.connection.commit()
        return cursor.rowcount > 0

    # region delete
    def delete_parking_lot(self, lot_id: int) -> bool:
        """
        Deletes a parking lot based on id
        @param: lot_id
        @return: True if deletion was successful
        """
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM parking_lots WHERE id = %s;", (lot_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    @staticmethod
    def map_to_parking_lot(cursor) -> List[ParkingLot]:
        """
        Maps the cursor to a list of parking lot objects
        @param: cursor
        @return: list of ParkingLot objects
        """
        columns = [desc[0] for desc in cursor.description]
        parking_lots = []
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            try:
                parking_lot = ParkingLot.model_validate(row_dict)
                parking_lots.append(parking_lot)
            except ValidationError  as e:
                print("Failed to map row to parking_lot:", row_dict, e)
        return parking_lots
