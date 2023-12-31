"""Loads detected changes into the db"""
# pylint: disable=invalid-name
from os import environ
from dotenv import load_dotenv
import pandas as pd
from psycopg2 import connect
from psycopg2.extensions import connection
from psycopg2.extras import execute_values
from extract import get_db_connection


TRANSFORMED_ARTICLES_FOR_ARTICLE_VERSION = "transformed_data_for_a_v.csv"
TRANSFORMED_ARTICLES_FOR_ARTICLE_CHANGE = "transformed_data_for_a_c.csv"


def add_to_article_version_table(conn: connection, df: pd.DataFrame) -> None:
    """Converts df into tuples, then adds to article_version table."""

    with conn.cursor() as cur:
        changes = df.to_records(index=False)
        execute_values(cur, """INSERT INTO article_version
                    (scraped_at, heading, body, article_id)
                    VALUES %s;""", changes)
        conn.commit()


def add_to_article_change_table(conn: connection, df: pd.DataFrame) -> None:
    """Converts df into tuples, then adds to article_change table."""

    with conn.cursor() as cur:
        changes = df.to_records(index=False)
        execute_values(cur, """INSERT INTO changes.article_change (article_id, \
                    article_url, change_type, previous_version, current_version,\
                    last_scraped, current_scraped, similarity) VALUES %s;""", \
                        changes)
        conn.commit()


def load_data() -> None:
    """Combines functions in load.py to execute whole load process"""

    try:
        load_dotenv()
        db_conn = get_db_connection()

        article_version = pd.read_csv(TRANSFORMED_ARTICLES_FOR_ARTICLE_VERSION)
        article_change = pd.read_csv(TRANSFORMED_ARTICLES_FOR_ARTICLE_CHANGE)

        if not article_version.empty:
            article_version["article_id"] = article_version["article_id"].map(str)
            add_to_article_version_table(db_conn, article_version)
        if not article_change.empty:
            article_change["article_id"] = article_change["article_id"].map(str)
            article_change["similarity"] = article_change["similarity"].map(str)
            add_to_article_change_table(db_conn, article_change)
    except KeyboardInterrupt:
        print("User stopped.")
    except pd.errors.EmptyDataError:
        print("No changes at this time")
    except Exception as exc:
        print(exc)
    finally:
        db_conn.close()


if __name__ == "__main__":

    load_data()
