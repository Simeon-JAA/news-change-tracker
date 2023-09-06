"""Comparison file to compare scraped data with data in the db"""

import pandas as pd

from extract import get_db_connection


SCRAPED_DATA_FOR_COMPARISON = "scraped_articles_for_comparison.csv"


def get_scraoed_data_as_df(file_path: str) -> pd.DataFrame:
    """Returns scraped data from extract"""

    return pd.read_csv(file_path)


def compare_data() -> None:
    """Compares scraped data with the data in the db and identifies where there are difference"""

    conn = get_db_connection()

    scraped_data = get_scraoed_data_as_df(SCRAPED_DATA_FOR_COMPARISON)

    print(scraped_data)

    conn.close()

if __name__ == "__main__":

    compare_data()