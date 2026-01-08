import psycopg2
from api.datatypes.discount_code import DiscountCodeCreate, DiscountCode
from api.session_calculator import generate_transaction_validation_hash


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
        cursor.execute("""
            INSERT INTO discount_codes
            (code, discount_type, discount_value, use_amount, end_date)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *;
        """,
                        (d.code, d.discount_type, d.discount_value, d.use_amount, d.end_date))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None


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


    def get_discount_code_by_did(self, id):
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM discount_codes WHERE id = %s;
                        """, (id,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
    

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


    def deactive_discount_code(self, id):
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE discount_codes
            SET active = FALSE
            WHERE id = %s
            RETURNING *;
        """, (id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None