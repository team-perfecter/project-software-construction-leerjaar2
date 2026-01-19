"""
This file stores the connection information for the database.
"""
import psycopg2
import os


def get_connection():
    """
    Returns a new connection to the database.
    Each call creates a fresh connection suitable for multithreaded use.
    """
    if os.environ.get("TESTING") == "1":
        host = "test_db"
        database = "test_database"
    else:
        host = "db"
        database = "database"
    return psycopg2.connect(
        host=host,
        port=5432,
        database=database,
        user="user",
        password="password",
    )