"""Loads detected changes into the db"""
# pylint: disable=invalid-name
import pandas as pd
from psycopg2.extensions import connection
from psycopg2.extras import execute_values
from extract import get_db_connection


TRANSFORMED_ARTICLES_FOR_DB = "transformed_data_for_db.csv"
TRANSFORMED_ARTICLES_FOR_S3 = "transformed_data_for_s3.csv"


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
        db_conn = get_db_connection()

        article_changes_db = pd.read_csv(TRANSFORMED_ARTICLES)

        if not article_changes_db.empty:
            article_changes_db["article_id"] = article_changes_db["article_id"].map(str)
            add_to_article_version_table(db_conn, article_changes_db)
    except KeyboardInterrupt:
        raise KeyboardInterrupt("Stopped by user")
    except Exception as exc:
        print(exc)
    finally:
        db_conn.close()


if __name__ == "__main__":

    load_data()
