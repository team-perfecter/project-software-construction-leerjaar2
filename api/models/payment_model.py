"""
This file contains all queries related to payments.
"""

import psycopg2
from api.datatypes.payment import PaymentCreate, PaymentUpdate


class PaymentModel:
    """
    Handles all database operations related to payments.

    Attributes:
        connection (psycopg2.connection): PostgreSQL database connection shared by all class methods.
    """
    connection = psycopg2.connect(
        host="db",
        port=5432,
        database="database",
        user="user",
        password="password",
    )

    @classmethod
    def create_payment(cls, p: PaymentCreate) -> bool:
        """
        Create a new payment record in the database.

        Args:
            p (PaymentCreate): Data for the payment to create.

        Returns:
            bool: True if the payment was successfully created, False otherwise.
        """
        cursor = cls.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO payments
                (user_id, transaction, amount, hash, method, issuer, bank)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """,
                           (p.user_id, p.transaction, p.amount,
                            p.hash, p.method, p.issuer, p.bank))
            created = cursor.fetchone()
            cls.connection.commit()
            print("Created:", created)
            return created is not None
        except Exception as e:
            print("DB Error:", e)
            cls.connection.rollback()
            return False

    @classmethod
    def get_payment_by_payment_id(cls, payment_id: int) -> dict | None:
        """
        Retrieve a single payment by its ID.

        Args:
            payment_id (int): The ID of the payment to retrieve.

        Returns:
            dict | None: Payment data as a dictionary, or None if not found.
        """
        cursor = cls.connection.cursor()
        cursor.execute("""
            SELECT * FROM payments WHERE id = %s;
        """, (payment_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    @classmethod
    def get_payments_by_user(cls, user_id: int) -> list[dict]:
        """
        Retrieve all payments for a specific user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list[dict]: List of payments as dictionaries. Empty list if none found.
        """
        cursor = cls.connection.cursor()
        cursor.execute("""
            SELECT * FROM payments WHERE user_id = %s;
        """, (user_id,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    @classmethod
    def get_open_payments_by_user(cls, user_id: int) -> list[dict]:
        """
        Retrieve all unpaid (open) payments for a specific user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list[dict]: List of unpaid payments as dictionaries.
        """
        cursor = cls.connection.cursor()
        cursor.execute("""
            SELECT * FROM payments WHERE user_id = %s AND completed IS FALSE;
        """, (user_id,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    @classmethod
    def update_payment(cls, payment_id: int, p: PaymentUpdate) -> bool:
        """
        Update an existing payment record.

        Args:
            payment_id (int): The ID of the payment to update.
            p (PaymentUpdate): The updated payment data.

        Returns:
            bool: True if the update succeeded, False otherwise.
        """
        cursor = cls.connection.cursor()
        cursor.execute("""
            UPDATE payments
            SET user_id = %s, transaction = %s, amount = %s,
                hash = %s, method = %s, issuer = %s, bank = %s, completed = %s,
                date = NOW(), refund_requested = %s
            WHERE id = %s
            RETURNING id;
        """, (p.user_id, p.transaction, p.amount,
              p.hash, p.method,
              p.issuer, p.bank, p.completed, p.refund_requested, payment_id,))
        updated = cursor.fetchone()
        cls.connection.commit()
        return updated is not None

    @classmethod
    def mark_payment_completed(cls, payment_id: int) -> bool:
        """
        Mark a payment as completed.

        Args:
            payment_id (int): The ID of the payment to mark as completed.

        Returns:
            bool: True if the payment was successfully updated, False otherwise.
        """
        cursor = cls.connection.cursor()
        cursor.execute("""
            UPDATE payments
            SET completed = TRUE
            WHERE id = %s
            RETURNING id;
        """, (payment_id,))
        updated = cursor.fetchone()
        cls.connection.commit()
        return updated is not None

    @classmethod
    def mark_refund_request(cls, payment_id: int) -> bool:
        """
        Mark a payment as having a refund requested.

        Args:
            payment_id (int): The ID of the payment to mark.

        Returns:
            bool: True if the update succeeded, False otherwise.
        """
        cursor = cls.connection.cursor()
        cursor.execute("""
            UPDATE payments
            SET refund_requested = TRUE
            WHERE id = %s
            RETURNING id;
        """, (payment_id,))
        updated = cursor.fetchone()
        cls.connection.commit()
        return updated is not None

    @classmethod
    def get_refund_requests(cls, user_id: int | None = None) -> list[dict]:
        """
        Retrieve all refund requests, optionally filtered by user.

        Args:
            user_id (int | None): Optional user ID to filter refunds.

        Returns:
            list[dict]: List of refund-requested payments.
        """
        cursor = cls.connection.cursor()
        query = """
            SELECT *
            FROM payments
            WHERE refund_requested = TRUE
        """
        user_ids = []
        if user_id is not None:
            query += " AND user_id = %s"
            user_ids.append(user_id)
        cursor.execute(query, user_ids)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    @classmethod
    def delete_payment(cls, payment_id: int) -> bool:
        """
        Delete a payment by its ID.

        Args:
            payment_id (int): The ID of the payment to delete.

        Returns:
            bool: True if the deletion succeeded, False otherwise.
        """
        cursor = cls.connection.cursor()
        cursor.execute("DELETE FROM payments WHERE id = %s RETURNING id;",
                       (payment_id,))
        deleted = cursor.fetchone()
        cls.connection.commit()
        return deleted is not None
