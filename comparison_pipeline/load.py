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
TRANSFORMED_ARTICLES_FOR_ARTICLE_CHANGES = "transformed_data_for_a_c.csv"


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
        heading_and_body_changes = df.to_records(index=False)
        execute_values(cur, """INSERT INTO article_version
                    (scraped_at, heading, body, article_id)
                    VALUES %s;""", heading_and_body_changes)
        conn.commit()


def add_to_article_version_table(conn: connection, df: pd.DataFrame) -> None:
    """Converts df into tuples, then adds to article_version table."""

    with conn.cursor() as cur:
        heading_and_body_changes = df.to_records(index=False)
        execute_values(cur, """INSERT INTO article_version
                    (scraped_at, heading, body, article_id)
                    VALUES %s;""", heading_and_body_changes)
        conn.commit()


def load_data() -> None:
    """Combines functions in load.py to execute whole load process"""

    try:
        load_dotenv()
        db_conn = get_db_connection()

        article_changes_db = pd.read_csv(TRANSFORMED_ARTICLES_FOR_DB)
        # article_changes_s3 = pd.read_csv(TRANSFORMED_ARTICLES_FOR_S3)

        # if not article_changes_db.empty:
        #     article_changes_db["article_id"] = article_changes_db["article_id"].map(str)
        #     add_to_article_version_table(db_conn, article_changes_db)
    except KeyboardInterrupt:
        raise KeyboardInterrupt("Stopped by user")
    except Exception as exc:
        print(exc)
    finally:
        db_conn.close()


if __name__ == "__main__":

    load_data()
