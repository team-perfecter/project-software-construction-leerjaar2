import os

import psycopg2
import json
import logging

from api.utilities.Hasher import hash_string

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

class DataConverter:
    def __init__(self):
        self.connection = psycopg2.connect(
            host="db",
            port=5432,
            database="database",
            user="user",
            password="password",
        )

        self.script_dir = os.path.dirname(os.path.abspath(__file__))

    def read_data(self, filename):
        filepath = os.path.join(self.script_dir, 'data', f'{filename}.json')
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        with open(filepath, 'r') as f:
            data = json.load(f)
        if data:
            return data
        else:
            logging.info("No data found")
            return None

    def insert_user(self, data):
        cursor = self.connection.cursor()
        for user in data:
            # Try to insert new user
            cursor.execute("""
                           INSERT INTO users (username, password, name, email, phone, birth_year, active, old_hash)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (username) DO NOTHING;
                           """, (
                               user['username'], user['password'], user['name'], user['email'],
                               user['phone'], user['birth_year'], True, True
                           ))

            # If insert did nothing (username exists), insert as inactive
            cursor.execute("""
                           INSERT INTO users (username, password, name, email, phone, birth_year, active, old_hash)
                           SELECT %s,
                                  %s,
                                  %s,
                                  %s,
                                  %s,
                                  %s,
                                  %s,
                                  %s WHERE NOT EXISTS (
                    SELECT 1 FROM users WHERE username = %s
                               );
                           """, (
                               user['username'], user['password'], user['name'], user['email'],
                               user['phone'], user['birth_year'], False, True,  # active=False
                               user['username']
                           ))
        self.connection.commit()
        cursor.close()

    def add_super_admin(self):
        # Check for superadmin
        cur = self.connection.cursor()
        cur.execute("SELECT id FROM users WHERE role = 'superadmin' LIMIT 1;")
        exists = cur.fetchone()

        if not exists:
            try:
                hashed_pw = hash_string("admin123")

                cur.execute("""
                            INSERT INTO users (username, password, name, email, role)
                            VALUES ('superadmin', %s, 'Super Admin', 'super@admin.com', 'superadmin');
                            """, (hashed_pw,))

                print("Default superadmin created.")
                self.connection.commit()

            except Exception as e:
                self.connection.rollback()
                print("Failed to create superadmin:", e)
        else:
            print("Superadmin already exists.")

    def convert(self):
        user_data = self.read_data('users')
        if not user_data:
            logging.info("No users data found, aborting conversion")
            return
        logging.info("Read the user data from json")
        self.insert_user(user_data)


