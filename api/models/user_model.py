from datetime import datetime

import psycopg2

from api.datatypes.user import UserCreate, User, UserLogin



class UserModel:
    def __init__(self):
        self.connection = psycopg2.connect(
            host="db",
            port=5432,
            database="database",
            user="user",
            password="password",
        )

    def create_user(self, user: UserCreate) -> None:
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO users (username, password, name, email, phone, birth_year)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (user.username, user.password, user.name, user.email, user.phone, user.birth_year))
        self.connection.commit()

    def get_user_by_id(self, user_id) -> User | None:
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM users WHERE id = %s;
            """, (user_id,))

        user_list = self.map_to_user(cursor)
        if len(user_list) > 0:
            return user_list[0]
        else:
            return None


    def get_user_by_username(self, username: str) -> User | None:
        if username is None:
            return None
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM users WHERE username = %s;
            """, (username,))

        user_list = self.map_to_user(cursor)
        if len(user_list) > 0:
            return user_list[0]
        else:
            return None

    def get_user_login(self, data: UserLogin) -> User | None:
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM users WHERE username = %s, password = %s;
            """, (data.username, data.password))

        user_list = self.map_to_user(cursor)
        if len(user_list) > 0:
            return user_list[0]
        else:
            return None

    def map_to_user(self, cursor):
        columns = [desc[0] for desc in cursor.description]
        return [User(**dict(zip(columns, row))) for row in cursor.fetchall()]