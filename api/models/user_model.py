"""
This file contains all queries related to users.
"""

import psycopg2
from api.datatypes.user import UserCreate, User, UserLogin


class UserModel:
    """
    Handles all database operations related to users.
    """

    def __init__(self):
        """
        Initialize a new UserModel instance and connect to the database.
        """
        self.connection = psycopg2.connect(
            host="db",
            port=5432,
            database="database",
            user="user",
            password="password",
        )

    def create_user(self, user: UserCreate) -> None:
        """
        Create a new user without specifying a role.

        Args:
            user (UserCreate): User data including username, password, name, email, phone, and birth_year.

        Returns:
            None
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO users (username, password, name, email, phone, birth_year)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (user.username, user.password, user.name, user.email, user.phone, user.birth_year))
        self.connection.commit()

    def create_user_with_role(self, user: UserCreate) -> None:
        """
        Create a new user and assign a role.

        Args:
            user (UserCreate): User data including username, password, name, email, phone, birth_year, and role.

        Returns:
            None
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO users (username, password, name, email, phone, birth_year, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (user.username,
              user.password,
              user.name,
              user.email,
              user.phone,
              user.birth_year,
              user.role))
        self.connection.commit()

    def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            User | None: The user object if found, otherwise None.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM users WHERE id = %s;
        """, (user_id,))

        user_list = self.map_to_user(cursor)
        return user_list[0] if user_list else None

    def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their username.

        Args:
            username (str): The username of the user.

        Returns:
            User | None: The user object if found, otherwise None.
        """
        if username is None:
            return None
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM users WHERE username = %s;
        """, (username,))
        user_list = self.map_to_user(cursor)
        return user_list[0] if user_list else None

    def get_user_login(self, data: UserLogin) -> User | None:
        """
        Retrieve a user for login verification.

        Args:
            data (UserLogin): Contains username and password for login.

        Returns:
            User | None: The user object if credentials match, otherwise None.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM users WHERE username = %s, password = %s;
        """, (data.username, data.password))

        user_list = self.map_to_user(cursor)
        return user_list[0] if user_list else None

    def get_all_users(self) -> list[User]:
        """
        Retrieve all users in the database.

        Returns:
            list[User]: List of all user objects.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM users;
        """)
        user_list = self.map_to_user(cursor)
        return user_list

    def update_user(self, user_id: int, update_data: dict) -> None:
        """
        Update an existing user's details.

        Args:
            user_id (int): The ID of the user to update.
            update_data (dict): Dictionary of fields to update with new values.

        Returns:
            None
        """
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

    def map_to_user(self, cursor) -> list[User]:
        """
        Map database rows to User objects.

        Args:
            cursor: The database cursor after executing a query.

        Returns:
            list[User]: List of User objects.
        """
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
        """
        Retrieve all parking lot IDs that a given admin can manage.

        Args:
            user_id (int): The ID of the admin user.

        Returns:
            list[int]: List of parking lot IDs.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT parking_lot_id 
            FROM parking_lot_admins 
            WHERE admin_user_id = %s;
        """, (user_id,))
        rows = cursor.fetchall()
        return [r[0] for r in rows]

    def add_parking_lot_access(self, admin_id: int, lot_id: int) -> None:
        """
        Grant an admin access to a specific parking lot.

        Args:
            admin_id (int): The admin user ID.
            lot_id (int): The parking lot ID.

        Returns:
            None
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO admin_parking_lots (admin_id, lot_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
        """, (admin_id, lot_id))
        self.connection.commit()

    def delete_user(self, user_id: int):
        """
        Delete a user from the database by their ID.

        Args:
            user_id (int): The ID of the user to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s RETURNING id;", (user_id,))
        deleted = cursor.fetchone()
        self.connection.commit()
        return deleted
