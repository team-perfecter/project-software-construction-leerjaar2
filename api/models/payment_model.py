from datetime import date

import psycopg2

from api.datatypes.payment import PaymentCreate, Payment


class PaymentModel:
    def init(self):
        self.connection = psycopg2.connect(
            host="localhost",
            port=5432,
            database="database",
            user="user",
            password="password",
        )

    def create_payment(self, p: PaymentCreate):
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO payments (user_id, transaction, amount, completed, hash, method, issuer, bank, date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (p.user_id, p.transaction, p.amount, p.completed, p.hash, p.method, p.issuer, p.bank, p.date))
        created = cursor.fetchone()
        self.connection.commit()
        return created is not None

    def get_payment_by_payment_id(self, id):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM payments WHERE user_id = %s;
                       """, id)
        return cursor.fetchone()

    def get_payments_by_user(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM payments WHERE user_id = %s;
                       """, user_id)
        return cursor.fetchall()
    
    def get_open_payments_by_user(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM payments WHERE user_id = %s AND completed = %s;
                       """, user_id, False)
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

        
            


