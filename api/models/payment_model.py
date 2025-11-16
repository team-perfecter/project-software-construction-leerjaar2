from datetime import date

import psycopg2

from api.datatypes.payment import PaymentCreate, Payment


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

    def get_payment_by_payment_id(self, id):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM payments WHERE id = %s;
                       """, (id,))
        return cursor.fetchone()

    @classmethod
    def get_payments_by_user(cls, user_id):
        cursor = cls.connection.cursor()
        cursor.execute("""
            SELECT * FROM payments WHERE user_id = %s;
                       """, (user_id,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]  # get column names
        result = [dict(zip(columns, row)) for row in rows]
        return result
    
    def get_open_payments_by_user(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM payments WHERE user_id = %s AND completed = %s;
                       """, (user_id, False))
        return cursor.fetchall()
    
    def update_payment(self, id, p: PaymentCreate):
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE payments 
            SET user_id = %s, transaction = %s, amount = %s, completed = %s, 
                hash = %s, method = %s, issuer = %s, bank = %s, date = %s
            WHERE id = %s
            RETURNING id;
        """, (p.user_id, p.transaction, p.amount, 
              p.completed, p.hash, p.method, 
              p.issuer, p.bank, p.date, id,))
        updated = cursor.fetchone()
        self.connection.commit()
        return updated is not None
    
    def mark_payment_completed(self, id):
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE payments
            SET completed = TRUE
            WHERE id = %s
            RETURNING id;
        """, (id,))
        updated = cursor.fetchone()
        self.connection.commit()
        return updated is not None


    def delete_payment(self, id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM payments WHERE id = %s RETURNING id;", (id,))
        deleted = cursor.fetchone()
        self.connection.commit()
        return deleted is not None

        
            


