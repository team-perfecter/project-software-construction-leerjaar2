import psycopg2
from api.datatypes.parking_lot import Parking_lot
from api.datatypes.session import Session
from typing import List, Optional


class ParkingLotModel:
    def __init__(self):
        self.connection = psycopg2.connect(
            host="db",
            port=5432,
            database="database",
            user="user",
            password="password",
        )

    # region get
    def get_all_parking_lots(self) -> List[Parking_lot]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM parking_lots;")
        return self.map_to_parking_lot(cursor)

    def get_parking_lot_by_lid(self, lot_id: int) -> Optional[Parking_lot]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM parking_lots WHERE id = %s;", (lot_id,))
        lots = self.map_to_parking_lot(cursor)
        return lots[0] if lots else None

    def get_all_sessions_by_lid(self, lot_id: int) -> List[Session]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sessions WHERE parking_lot_id = %s;", (lot_id,))
        return self.map_to_session(cursor)

    def get_session_by_lid_and_sid(
        self, lot_id: int, session_id: int
    ) -> Optional[Session]:
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM sessions WHERE parking_lot_id = %s AND id = %s;",
            (lot_id, session_id),
        )
        sessions = self.map_to_session(cursor)
        return sessions[0] if sessions else None

    def map_to_session(self, cursor) -> List[Session]:
        columns = [desc[0] for desc in cursor.description]
        sessions = []
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            try:
                session = Session.model_validate(row_dict)
                sessions.append(session)
            except Exception as e:
                print("Failed to map row to Session:", row_dict, e)
        return sessions

    def find_parking_lots(
        self,
        lot_id: int = None,
        name: str = None,
        location: str = None,
        city: str = None,
        min_capacity: int = None,
        max_capacity: int = None,
        min_tariff: float = None,
        max_tariff: float = None,
        has_availability: bool = None,
    ) -> List[Parking_lot]:
        cursor = self.connection.cursor()

        query = "SELECT * FROM parking_lots WHERE 1=1"
        params = []

        if lot_id is not None:
            query += " AND id = %s"
            params.append(lot_id)

        if name is not None:
            query += " AND name ILIKE %s"
            params.append(f"%{name}%")

        if location is not None:
            query += " AND location ILIKE %s"
            params.append(f"%{location}%")

        if city is not None:
            query += " AND SPLIT_PART(address, ' ', -1) ILIKE %s"
            params.append(f"%{city}%")

        if min_capacity is not None:
            query += " AND capacity >= %s"
            params.append(min_capacity)

        if max_capacity is not None:
            query += " AND capacity <= %s"
            params.append(max_capacity)

        if min_tariff is not None:
            query += " AND tariff >= %s"
            params.append(min_tariff)

        if max_tariff is not None:
            query += " AND tariff <= %s"
            params.append(max_tariff)

        if has_availability is not None and has_availability:
            query += " AND (capacity - reserved) > 0"

        query += ";"

        cursor.execute(query, params)
        return self.map_to_parking_lot(cursor)

    # region post
    def create_parking_lot(self, lot: Parking_lot) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO parking_lots 
            (name, location, address, capacity, reserved, tariff, daytariff, created_at, lat, lng, status, closed_reason, closed_date)
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
    def update_parking_lot(self, lot_id: int, lot: Parking_lot) -> bool:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE parking_lots 
            SET name = %s, location = %s, address = %s, capacity = %s, 
                reserved = %s, tariff = %s, daytariff = %s, lat = %s, lng = %s,
                status = %s, closed_reason = %s, closed_date = %s
            WHERE id = %s;
        """,
            (
                lot.name,
                lot.location,
                lot.address,
                lot.capacity,
                lot.reserved,
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

    # region delete
    def delete_parking_lot(self, lot_id: int) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM parking_lots WHERE id = %s;", (lot_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def map_to_parking_lot(self, cursor) -> List[Parking_lot]:
        columns = [desc[0] for desc in cursor.description]
        parking_lots = []
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            try:
                user = Parking_lot.model_validate(row_dict)
                parking_lots.append(user)
            except Exception as e:
                print("Failed to map row to User:", row_dict, e)
        return parking_lots
