from datetime import date

import psycopg2

from api.datatypes.payment import PaymentCreate, PaymentUpdate


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
        try:
            cursor.execute("""
                INSERT INTO payments (user_id, transaction, amount, hash, method, issuer, bank)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (p.user_id, p.transaction, p.amount, p.hash, p.method, p.issuer, p.bank))
            created = cursor.fetchone()
            cls.connection.commit()
            print("Created:", created)
            return created is not None
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
    def update_payment(cls, id, p: PaymentUpdate):
        cursor = cls.connection.cursor()
        cursor.execute("""
            UPDATE payments 
            SET user_id = %s, transaction = %s, amount = %s, 
                hash = %s, method = %s, issuer = %s, bank = %s, completed = %s, date = NOW()
            WHERE id = %s
            RETURNING id;
        """, (p.user_id, p.transaction, p.amount, 
            p.hash, p.method, 
              p.issuer, p.bank, p.completed, id,))
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
    def delete_payment(cls, id):
        cursor = cls.connection.cursor()
        cursor.execute("DELETE FROM payments WHERE id = %s RETURNING id;", (id,))
        deleted = cursor.fetchone()
        cls.connection.commit()
        return deleted is not None

        
            


