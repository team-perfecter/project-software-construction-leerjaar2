import psycopg2
from api.datatypes.discount_code import DiscountCodeCreate


class DiscountCodeModel:
    def __init__(self):
        self.connection = psycopg2.connect(
            host="db",
            port=5432,
            database="database",
            user="user",
            password="password",
        )

    def create_discount_code(self, d: DiscountCodeCreate):
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO discount_codes
                (code, discount_type, discount_value,
                 use_amount, minimum_price,
                 start_applicable_time, end_applicable_time,
                 start_date, end_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *;
            """,
                           (
                            d.code, d.discount_type, d.discount_value,
                            d.use_amount, d.minimum_price,
                            d.start_applicable_time, d.end_applicable_time,
                            d.start_date, d.end_date
                           ))
            row = cursor.fetchone()
            self.add_discount_code_locations(d.code, d.locations or [])
            if row:
                columns = [desc[0] for desc in cursor.description]
                self.connection.commit()
                return dict(zip(columns, row))
            self.connection.commit()
            return None
        except Exception:
            self.connection.rollback()
            raise

    def add_discount_code_locations(self, discount_code: str,
                                    locations: list[str]):
        if not locations:
            return

        cursor = self.connection.cursor()
        for loc in set(locations):
            cursor.execute("""
                INSERT INTO discount_code_locations (discount_code, location)
                VALUES (%s, %s)
                ON CONFLICT (discount_code, location) DO NOTHING;
            """, (discount_code, loc))
        self.connection.commit()

    def get_all_discount_codes(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM discount_codes;
                       """)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        return result

    def get_all_active_discount_codes(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM discount_codes WHERE active IS TRUE;
                       """)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        return result

    def get_discount_code_by_code(self, code):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM discount_codes WHERE code = %s;
                    """, (code,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    def get_all_locations_by_code(self, code):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT location FROM discount_code_locations
            WHERE discount_code = %s;
                    """, (code,))
        rows = cursor.fetchall()
        return [row[0] for row in rows] if rows else []

    def deactivate_discount_code(self, code):
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE discount_codes
            SET active = FALSE
            WHERE code = %s
            RETURNING *;
        """, (code,))
        row = cursor.fetchone()
        self.connection.commit()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    def delete_discount_code(self, code):
        cursor = self.connection.cursor()
        cursor.execute("""
            DELETE FROM discount_codes
            WHERE code = %s
            RETURNING *;
        """, (code,))
        row = cursor.fetchone()
        self.connection.commit()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    def update_discount_code(self, code: str, update_data: dict):
        if not code or not update_data:
            return

        cursor = self.connection.cursor()

        set_clauses = ", ".join(
            f"{key} = %s" for key in update_data.keys()
        )
        values = list(update_data.values()) + [code]
        try:
            cursor.execute(f"""
                UPDATE discount_codes
                SET {set_clauses}
                WHERE code = %s
                RETURNING *;
            """, values)
            row = cursor.fetchone()
            self.connection.commit()
            if row:
                columns = [desc[0] for desc in cursor.description]
                self.connection.commit()
                return dict(zip(columns, row))
        except Exception:
            self.connection.rollback()
            raise

    def increment_used_count(self, code):
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE discount_codes
            SET used_count = used_count + 1
            WHERE code = %s
            RETURNING *;
        """, (code,))
        row = cursor.fetchone()
        self.connection.commit()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
