"""Handles all load functions that load data and information into the database"""
# pylint: disable=invalid-name
from os import environ
import datetime
import re
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


def get_connected_locally():
    """Connectivity function for local database"""
    load_dotenv()
    conn = connect(\
    user = environ["LOCAL_USER"],
    host = environ["LOCAL_IP"],
    password = environ["LOCAL_PASSWORD"],
    port = environ["DB_PORT"],
    database = environ["DB_NAME"])
    return conn



def get_data_from_db(conn: connection, table: str, column = "*")-> pd.DataFrame:
    """Connects to the database and returns dataframe of selected table and column(s)"""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT {column} FROM {table};""")
        result = cur.fetchall()

    return pd.DataFrame(result)


def check_for_duplicate_articles(conn: connection, url: str) -> str:
    """Checks for a duplicates in article table. Returns a dataframe without duplicates."""

    with conn.cursor() as cur:
        cur.execute("""SELECT * FROM article where article_url = %s;""", [url])
        duplicate = cur.fetchall()
        if len(duplicate) > 0:
            return None
    return url


def check_for_duplicate_authors(conn: connection, name: str) -> str:
    """Checks for a duplicates in author table. Returns a dataframe without duplicates."""

    with conn.cursor() as cur:
        cur.execute("""SELECT * FROM author where author_name = %s;""", [name])
        duplicate = cur.fetchall()
        if len(duplicate) > 0:
            return None
    return name


def add_to_article_table_from_pandas(conn: connection, df: pd.DataFrame) -> None:
    """Converts df into tuples, then adds to article table.
    NB: needs author column converted into foreign key reference"""

    with conn.cursor() as cur:
        tuples = df.to_records(index=False)
        execute_values(cur, """INSERT INTO article (article_url, source, created_at)
                       VALUES %s;""", tuples)
        conn.commit()


def add_to_scraping_info_table_from_pandas(conn: connection, df: pd.DataFrame) -> None:
    """Converts df into tuples, then adds to scraping_info table.
    NB: needs article_id column converted into foreign key reference"""

    with conn.cursor() as cur:
        tuples = df.to_records() # is this a list?
        execute_values(cur, """INSERT INTO scraping_info (scraped_at, title, body,
                       article_id) VALUES (%s)""", tuples)
        conn.commit()

# hardcode source

def add_to_author_table(conn: connection, df: pd.DataFrame) -> None:
    """Converts df into tuples, then adds to authors table.
    NB: needs article_id column converted into foreign key reference"""

    with conn.cursor() as cur:
        tuples = df.to_records(index=False)
        execute_values(cur, """INSERT INTO author (author_name) VALUES %s;""", tuples)
        conn.commit()


def load_data():
    """Complete data loading in one function. Used for main.py"""
    db_conn = get_connected_locally()
    df_transformed = pd.read_csv(TRANSFORMED_DATA)

    # removes duplicates
    df_transformed["url"] = df_transformed["url"].apply\
        (lambda x: check_for_duplicate_articles(db_conn, x))
    df_transformed = df_transformed.dropna(subset=["url"])

    # inserts articles
    df_for_article = df_transformed[["url", "author", "published"]].copy()
    df_for_article["author"] = "BBC"
    add_to_article_table_from_pandas(db_conn, df_for_article)
    print(df_for_article)

    # inserts authors
    df_for_author = df_transformed[["author"]].copy()
    df_for_author["author"] = df_for_author["author"].apply(lambda x: re.findall("'([^']*)'", x))
    df_for_author = df_for_author.explode(column=["author"]).dropna()
    df_for_author["author"] = df_for_author["author"].apply\
        (lambda x: check_for_duplicate_authors(db_conn, x))
    df_for_author = df_for_author.dropna()
    add_to_author_table(db_conn, df_for_author)
    print(df_for_author)

    db_conn.close()


if __name__ == "__main__":
    load_data()
