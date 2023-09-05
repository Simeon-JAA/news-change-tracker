"""Handles all load functions that load data and information into the database"""
# pylint: disable=invalid-name
from os import environ
import datetime
import pandas as pd
from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extensions import connection
from psycopg2.extras import execute_values

TRANSFORMED_DATA = "transformed_data.csv"
TIME_NOW = datetime.datetime.now()

def get_db_connection() -> connection:
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

    return None


def get_data_from_db(conn: connection, table: str, column = "*")-> pd.DataFrame:
    """Connects to the database and returns dataframe of selected table and column(s)"""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT {column} FROM {table};""")
        result = cur.fetchall()

    return pd.DataFrame(result)


def check_for_duplicates(conn: connection, df: pd.DataFrame, table: str, df_column: str, db_column) \
    -> pd.DataFrame:
    """Checks a local dataframe against a database table on specific column.
    Returns non-duplicative local data only"""
    df = df.copy()
    articles = get_data_from_db(conn, table)
    df = df[not df[df_column].isin(articles[db_column])]
    # test this line

    return df


def add_to_article_table_from_pandas(conn: connection, df: pd.DataFrame) -> None:
    """Converts df into tuples, then adds to article table.
    NB: needs author column converted into foreign key reference"""

    with conn.cursor() as cur:
        tuples = df.itertuples() # is this a list?
        execute_values(cur, """INSERT INTO author (article_url, source, created_at,
                       author) VALUES %s""", tuples)
        cur.commit()


def add_to_scraping_info_table_from_pandas(conn: connection, df: pd.DataFrame) -> None:
    """Converts df into tuples, then adds to scraping_info table.
    NB: needs article_id column converted into foreign key reference"""

    with conn.cursor() as cur:
        tuples = df.itertuples() # is this a list?
        execute_values(cur, """INSERT INTO scraping_info (scraped_at, title, body,
                       article_id) VALUES %s""", tuples)
        cur.commit()

# hardcode source

def add_to_authors_table_from_pandas(conn: connection, df: pd.DataFrame) -> None:
    """Converts df into tuples, then adds to authors table.
    NB: needs article_id column converted into foreign key reference"""
    pass


if __name__ == "__main__":
    db_conn = get_db_connection()
    df_transformed = pd.read_csv(TRANSFORMED_DATA)
    print(df_transformed)


    df_no_duplicates = check_for_duplicates(db_conn, df_transformed, "article", "url", "article_url")
    db_conn.close()
