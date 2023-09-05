"""Handles all load functions that load data and information into the database"""

from os import environ
import pandas as pd
from dotenv import load_dotenv
from psycopg2 import connect, OperationalError
from psycopg2.extensions import connection

TRANSFORMED_DATA = ""

def get_db_connection() -> connection:
    """Returns connection to the rds database"""
    load_dotenv()
    try:
        return connect(host=environ["DB_HOST"],
                   user=environ["DB_USER"],
                   password=environ["DB_PASSWORD"],
                   port=environ["DB_PORT"],
                   dbname=environ["DB_NAME"])
    except OperationalError:
        print("Failed to connect to database.")
        raise OperationalError()
    except Exception as exc:
        print(f"get_db_connection Error: {exc}")


def get_data_from_db(conn: connection, table: str, column = "*")-> pd.DataFrame:
    """Connects to the database and returns dataframe of selected table and column(s)"""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT {column} FROM {table};""")
        result = cur.fetchall()

    return pd.DataFrame(result)


def check_for_duplicates(conn: connection, df: pd.DataFrame) -> pd.DataFrame:
    """Checks the incoming articles for duplication in the database. Returns only fresh articles"""
    df = df.copy()
    articles = get_data_from_db(conn, "article")
    df = df[not df["article_url"].isin(articles["article_url"])]
    # test this line

    return df


if __name__ == "__main__":
    conn = get_db_connection()
    print(get_data_from_db(conn, "article", column="article_url, article_id"))
    df = pd.read_csv(TRANSFORMED_DATA)
    conn.close()
