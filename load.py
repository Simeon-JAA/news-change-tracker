"""Handles all load functions that load data and information into the database"""

from os import environ

from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extensions import connection, cursor


def get_db_connection(config) -> connection:
    """Returns connection to the rds database"""
    return connect(host=config["DB_HOST"],
                   user=config["DB_USER"],
                   password=config["DB_PASSWORD"],
                   port=config["DB_PORT"],
                   dbname=config["DB_NAME"])


if __name__ == "__main__":
    load_dotenv()

    config = environ

    conn = get_db_connection(config)

    print(conn)

    conn.close()
