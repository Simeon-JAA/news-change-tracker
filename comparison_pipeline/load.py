"""Loads detected changes into the db"""

from datetime import datetime

import pandas as pd
from psycopg2.extensions import connection

from extract import get_db_connection


ARTICLE_CHANGES = "article_changes.csv"


def get_article_changes_df(file_name: str) -> pd.DataFrame:
    """Returns detected changes csv as a df"""

    return pd.read_csv(file_name)


def add_to_article_version_table(conn: connection, df: pd.DataFrame) -> None:
    """Converts df into tuples, then adds to article_version table."""

    heading_and_body_changes = df.to_records()

    current_time = datetime.now().replace(microsecond=0)

    with conn.cursor() as cur:
        for article_change in heading_and_body_changes:
            print(article_change)
            cur.execute("""INSERT INTO article_version
                        (article_id, heading, body, scraped_at)
                        VALUES
                        (%s, %s, %s, %s);""",
                        [int(article_change[0]), article_change[1], article_change[2], current_time])

        conn.commit()


def insert_changes_into_db(conn: connection, df: pd.DataFrame) -> None:
    """Inserts any detected changes into the db"""

    # TODO insert body and heading into the db

    heading_and_body_df = df[["article_id",
                              "heading", "body_y"]].set_index("article_id")

    add_to_article_version_table(conn, heading_and_body_df)

    # TODO associate any new authors with the authors and article_authors table
    return


def load_data() -> None:
    """Combines functions in load.py to execute whole load process"""

    conn = get_db_connection()

    article_changes_db = get_article_changes_df(ARTICLE_CHANGES)

    insert_changes_into_db(conn, article_changes_db)

    conn.close()


if __name__ == "__main__":

    load_data()
