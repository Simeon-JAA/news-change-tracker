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


def check_for_duplicate_articles(conn: connection, url: str) -> str:
    """Checks for a duplicates in article table. Returns None if duplicate found."""

    with conn.cursor() as cur:
        cur.execute("""SELECT * FROM article where article_url = %s;""", [url])
        duplicate = cur.fetchall()
        if len(duplicate) > 0:
            return None
    return url


def check_for_duplicate_authors(conn: connection, name: str) -> str:
    """Checks for a duplicates in author table. Returns None if duplicate found."""

    with conn.cursor() as cur:
        cur.execute("""SELECT * FROM author where author_name = %s;""", [name])
        duplicate = cur.fetchall()
        if len(duplicate) > 0:
            return None
    return name


def add_to_article_table(conn: connection, df: pd.DataFrame) -> None:
    """Converts df into tuples, then adds to article table.
    NB: needs author column converted into foreign key reference"""

    with conn.cursor() as cur:
        tuples = df.to_records(index=False)
        execute_values(cur, """INSERT INTO article (article_url, source, created_at)
                       VALUES %s;""", tuples)
        conn.commit()


def add_to_article_author_table(conn: connection, df: pd.DataFrame) -> None:
    """Converts df into tuples, then adds to author_article table.
    NB: needs author and article columns converted into foreign key reference"""

    with conn.cursor() as cur:
        tuples = df.to_records(index=False)
        execute_values(cur, """INSERT INTO article_author (article_id, author_id)
                       VALUES %s;""", tuples)
        conn.commit()


def add_to_scraping_info_table(conn: connection, df: pd.DataFrame) -> None:
    """Converts df into tuples, then adds to scraping_info table.
    NB: needs article_id column converted into foreign key reference"""

    with conn.cursor() as cur:
        tuples = df.to_records(index=False)
        execute_values(cur, """INSERT INTO scraping_info (scraped_at, title, body,
                       article_id) VALUES %s""", tuples)
        conn.commit()


def retrieve_author_id(conn: connection, name: str) -> str:
    """Retrieves author_id from author table."""

    with conn.cursor() as cur:
        cur.execute("""SELECT author_id from author where author_name = %s""", [name])
        author_id = cur.fetchall()
        if len(author_id) == 1:
            return author_id[0][0]
    return None


def retrieve_article_id(conn: connection, url: str) -> str:
    """Retrieves article_id from author table."""

    with conn.cursor() as cur:
        cur.execute("""SELECT article_id from article where article_url = %s""", [url])
        url = cur.fetchall()
        if len(url) == 1:
            return url[0][0]
    return None


def add_to_author_table(conn: connection, df: pd.DataFrame) -> None:
    """Converts df into tuples, then adds to authors table.
    NB: needs article_id column converted into foreign key reference"""

    with conn.cursor() as cur:
        tuples = df.to_records(index=False)
        execute_values(cur, """INSERT INTO author (author_name) VALUES %s;""", tuples)
        conn.commit()


def add_to_article_version_table(conn: connection, df: pd.DataFrame) -> None:
    """Converts df into tuples, then adds to article_version table.
    NB: needs article_id column converted into foreign key reference"""

    with conn.cursor() as cur:
        tuples = df.to_records(index=False)
        execute_values(cur, """INSERT INTO article_version (scraped_at, heading, body, article_id)\
                 VALUES %s;""", tuples)
        conn.commit()


def load_data():
    """Complete data loading in one function. Used for main.py"""
    db_conn = get_db_connection()
    df_transformed = pd.read_csv(TRANSFORMED_DATA)

        # removes duplicates
        df_transformed["url"] = df_transformed["url"].apply\
            (lambda x: check_for_duplicate_articles(db_conn, x))
        df_transformed = df_transformed.dropna(subset=["url"])

        # inserts articles
        df_for_article = df_transformed[["url", "author", "published"]].copy()
        df_for_article["author"] = "BBC"
        add_to_article_table(db_conn, df_for_article)

        # inserts authors
        df_for_author = df_transformed[["author"]].copy().dropna()
        df_for_author["author"] = df_for_author["author"].apply(lambda x: re.findall("'([^']*)'", x))
        df_for_author = df_for_author.explode(column=["author"]).dropna()
        df_for_author = df_for_author.drop_duplicates(subset=["author"])
        df_for_author["author"] = df_for_author["author"].apply\
            (lambda x: check_for_duplicate_authors(db_conn, x))
        df_for_author = df_for_author.dropna()
        df_for_author.to_csv("author.csv")
        add_to_author_table(db_conn, df_for_author)

        # inserts article-author table entries
        df_author_article = df_transformed[["url", "author"]].copy().dropna()
        df_author_article["author"] = df_author_article["author"].apply\
            (lambda x: re.findall("'([^']*)'", x))
        df_author_article = df_author_article.explode(column=["author"]).dropna()
        df_author_article.to_csv("author_article.csv")
        df_author_article["url"] = df_author_article["url"].apply\
            (lambda x: retrieve_article_id(db_conn, x)).map(str)
        df_author_article["author"] = df_author_article["author"].apply\
            (lambda x: retrieve_author_id(db_conn, x)).map(str)
        add_to_article_author_table(db_conn, df_author_article)

        # insert article_version
        df_for_version = df_transformed[["published", "title", "body", "url"]].copy()
        df_for_version["url"] = df_for_version["url"].apply\
            (lambda x: retrieve_article_id(db_conn, x)).map(str)
        df_for_version["published"] = str(TIME_NOW)
        add_to_article_version_table(db_conn, df_for_version)
    except Exception as exc:
        print(exc)
    finally:
        db_conn.close()


    if __name__ == "__main__":
        load_data()
