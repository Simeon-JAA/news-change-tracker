"""Loads detected changes into the db"""
# pylint: disable=invalid-name
from os import environ
from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extensions import connection
import pandas as pd
from psycopg2.extensions import connection
from psycopg2.extras import execute_values


TRANSFORMED_ARTICLES_FOR_ARTICLE_VERSION = "transformed_data_for_a_v.csv"
TRANSFORMED_ARTICLES_FOR_ARTICLE_CHANGE = "transformed_data_for_a_c.csv"


def get_db_connection() -> connection:
    """Returns connection to the rds database"""

    return connect(host=environ["DB_HOST"],
                       user=environ["DB_USER"],
                       password=environ["DB_PASSWORD"],
                       port=environ["DB_PORT"],
                       dbname=environ["DB_NAME"])


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
        execute_values(cur, """INSERT INTO article_change (article_url, change_type,
                        previous_version, current_version, last_scraped, \
                       current_scraped, proportion_changed) VALUES %s;""", \
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
            add_to_article_change_table(db_conn, article_change)

    except KeyboardInterrupt:
        raise KeyboardInterrupt("Stopped by user")
    except Exception as exc:
        print(exc)
    finally:
        db_conn.close()


if __name__ == "__main__":

    load_data()
