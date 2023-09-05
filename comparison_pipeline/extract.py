"""Extraction file for comparison pipeline"""
from os import environ
from dotenv import load_dotenv
from psycopg2 import connect, OperationalError
from psycopg2.extensions import Connection
import pandas as pd


def get_db_connection() -> Connection:
    """Returns connection to the rds database"""
    load_dotenv()
    try:
        return connect(host=environ["DB_HOST"],
                   user=environ["DB_USER"],
                   password=environ["DB_PASSWORD"],
                   port=environ["DB_PORT"],
                   dbname=environ["DB_NAME"])
    except Exception as exc:
        print(f"get_db_connection Error: {exc}")
        raise Exception()


def get_data_from_db(conn: Connection, table: str)-> pd.DataFrame:
    """Connects to the database and returns dataframe of selected table"""
    with conn.cursor() as cur:
        cur.execute("""SELECT * FROM %s;""", [table])
        result = cur.fetchall()

    return pd.DataFrame(result)


if __name__ == "__main__":
    conn = get_db_connection()

    conn.close()