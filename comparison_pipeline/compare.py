"""Comparison file to compare scraped data with data in the db"""

import pandas as pd
from psycopg2.extensions import connection

from extract import get_db_connection


SCRAPED_DATA_FOR_COMPARISON = "transformed_data.csv"


def get_scraped_data_as_df(file_path: str) -> pd.DataFrame:
    """Returns scraped data from extract"""

    return pd.read_csv(file_path)


def get_scraped_data_from_db(conn: connection) -> pd.DataFrame:
    """Returns data from rds database in a dataframe for comparison"""

    cur = conn.cursor()

    cur.execute("""SELECT 
                    test.article.article_id,
                    test.article.source,
                    test.article.article_url,
                    test.scraping_info.heading,
                    test.scraping_info.body
                    FROM test.article
                    LEFT JOIN test.scraping_info
                    ON test.scraping_info.article_id = test.article.article_id;""")

    data = cur.fetchall()

    return pd.DataFrame(data, 
                        columns=["article_id", "source",
                                 "article_url", "heading", "body"])


def compare_data() -> None:
    """Compares scraped data with the data in the db and identifies where there are difference"""

    conn = get_db_connection()

    scraped_data = get_scraped_data_as_df(SCRAPED_DATA_FOR_COMPARISON)

    article_data_in_db = get_scraped_data_from_db(conn)

    conn.close()


if __name__ == "__main__":

    compare_data()
