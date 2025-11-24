from datetime import datetime

import psycopg2

from api.datatypes.user import UserCreate, User, UserLogin, UserUpdate, AdminCreate


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

    def create_admin(self, user: AdminCreate) -> None:
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO users (username, password, name, email, phone, birth_year, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (user.username, user.password, user.name, user.email, user.phone, user.birth_year, "admin"))
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

    def update_user(self, user_id: int, update_data: dict) -> None:
        if user_id is None or update_data is None:
            return

        cursor = self.connection.cursor()

        set_clauses = ", ".join(f"{key} = %s" for key in update_data.keys())
        values = list(update_data.values()) + [user_id]

        cursor.execute(f"""
            UPDATE users
            SET {set_clauses}
            WHERE id = %s;
        """, values)
        self.connection.commit()

    def map_to_user(self, cursor):
        columns = [desc[0] for desc in cursor.description]
        users = []
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            try:
                user = User.parse_obj(row_dict)
                users.append(user)
            except Exception as e:
                print("Failed to map row to User:", row_dict, e)
        return users
    
    def get_parking_lots_for_admin(self, user_id: int) -> list[int]:
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT parking_lot_id 
            FROM parking_lot_admins 
            WHERE admin_user_id = %s;
        """, (user_id,))
        rows = cursor.fetchall()
        return [r[0] for r in rows]