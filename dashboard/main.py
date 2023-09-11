"""Dashboard script"""

from os import environ
from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extensions import connection


def get_db_connection() -> connection:
    """Returns connection to the rds database"""

    load_dotenv()

    return connect(host=environ["DB_HOST"],
                       user=environ["DB_USER"],
                       password=environ["DB_PASSWORD"],
                       port=environ["DB_PORT"],
                       dbname=environ["DB_NAME"])


def display() -> None:
    """Displays the dashboard"""



if __name__ == "__main__":
    display()
