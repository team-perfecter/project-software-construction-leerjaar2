import psycopg2
from api.datatypes.payment import PaymentCreate
from api.session_calculator import generate_transaction_validation_hash


class PaymentModel:
    connection = psycopg2.connect(
        host="db",
        port=5432,
        database="database",
        user="user",
        password="password",
    )

    @classmethod
    def create_payment(cls, p: PaymentCreate):
        cursor = cls.connection.cursor()
        payment_hash = generate_transaction_validation_hash()
        try:
            cursor.execute("""
                INSERT INTO payments
                (user_id, parking_lot_id, reservation_id, session_id,
                transaction, amount, hash, method, issuer, bank)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """,
                           (p.user_id, p.parking_lot_id, p.reservation_id,
                            p.session_id, p.transaction, p.amount,
                            payment_hash, p.method, p.issuer, p.bank))
            created = cursor.fetchone()
            cls.connection.commit()
            print("Created:", created)
            if created:
                return created[0]
        except Exception as e:
            print("DB Error:", e)
            cls.connection.rollback()
            return False

    @classmethod
    def get_payment_by_payment_id(cls, id):
        cursor = cls.connection.cursor()
        cursor.execute("""
            SELECT * FROM payments WHERE id = %s;
                       """, (id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    @classmethod
    def get_payments_by_user(cls, user_id):
        cursor = cls.connection.cursor()
        cursor.execute("""
            SELECT * FROM payments WHERE user_id = %s;
                       """, (user_id,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        return result

    @classmethod
    def get_open_payments_by_user(cls, user_id):
        cursor = cls.connection.cursor()
        cursor.execute("""
            SELECT * FROM payments WHERE user_id = %s AND completed IS FALSE;
                       """, (user_id,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        return result

    @classmethod
    def update_payment(cls, payment_id: int, update_data: dict):
        if not payment_id or not update_data:
            return

        cursor = cls.connection.cursor()

        set_clauses = ", ".join(f"{key} = %s" for key in update_data.keys())
        values = list(update_data.values()) + [payment_id]

        cursor.execute(f"""
            UPDATE payments
            SET {set_clauses}
            WHERE id = %s
            RETURNING id;
        """, values)
        updated = cursor.fetchone()
        cls.connection.commit()
        return updated is not None

    @classmethod
    def mark_payment_completed(cls, id):
        cursor = cls.connection.cursor()
        cursor.execute("""
            UPDATE payments
            SET completed = TRUE
            WHERE id = %s
            RETURNING id;
        """, (id,))
        updated = cursor.fetchone()
        cls.connection.commit()
        return updated is not None

    @classmethod
    def mark_refund_request(cls, id):
        cursor = cls.connection.cursor()
        cursor.execute("""
            UPDATE payments
            SET refund_requested = TRUE
            WHERE id = %s
            RETURNING id;
        """, (id,))
        updated = cursor.fetchone()
        cls.connection.commit()
        return updated is not None

    @classmethod
    def give_refund(cls, user_id, id):
        cursor = cls.connection.cursor()
        cursor.execute("""
            UPDATE payments
            SET refund_accepted = TRUE, admin_id = %s
            WHERE id = %s
            RETURNING id;
        """, (user_id, id,))
        updated = cursor.fetchone()
        cls.connection.commit()
        return updated is not None

    @classmethod
    def get_refund_requests(cls, user_id: int | None = None):
        cursor = cls.connection.cursor()

        query = """
            SELECT *
            FROM payments
            WHERE refund_requested = TRUE, refund_accepted = FALSE
        """
        user_ids = []

        if user_id is not None:
            query += " AND user_id = %s"
            user_ids.append(user_id)

        cursor.execute(query, user_ids)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        return result

    @classmethod
    def delete_payment(cls, id):
        cursor = cls.connection.cursor()
        cursor.execute("DELETE FROM payments WHERE id = %s RETURNING id;",
                       (id,))
        deleted = cursor.fetchone()
        cls.connection.commit()
        return deleted is not None

    @classmethod
    def get_payment_by_reservation_id(cls, reservation_id):
        cursor = cls.connection.cursor()
        cursor.execute("SELECT * FROM payments WHERE reservation_id = %s;",
                       (reservation_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
