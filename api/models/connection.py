"""
This file stores the connection information for the database.
"""
import psycopg2

def get_connection():
    """
    Returns a new connection to the database.
    Each call creates a fresh connection suitable for multithreaded use.
    """
    return psycopg2.connect(
            host="db",
            port=5432,
            database="database",
            user="user",
            password="password",
        )
