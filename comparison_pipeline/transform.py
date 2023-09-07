"""Transforms the data by cleaning and adding necessary fields before it goes to comparison stage"""

import pandas as pd


SCRAPED_DATA_FOR_COMPARISON = "scraped_articles_for_comparison.csv"
SCRAPED_DATA_TO_CSV_NAME = "scraped_articles_for_comparison_transformed.csv"


def get_scraped_data_as_df(file_path: str) -> pd.DataFrame:
    """Returns scraped data as df before cleaning"""

    return pd.read_csv(file_path)


def format_authors(authors: str) -> list[str]:
    """Returns a list of authors if they exist and ['No Author'] if none detected"""

    if authors.lower() == "nan":
        return None

    if authors[:3].lower() == "by ":
        authors = authors.lower().replace("by ", "", 1).replace(" &", ",")
        authors = authors.replace(" and", ",")
        authors = authors.split(", ")
        authors.sort()

        authors = list(map(lambda author: author.title(), authors))

        return authors


def format_scraped_articles_df(scraped_articles_df: pd.DataFrame) -> pd.DataFrame:
    """Formats scraped_articles dataframe columns before saving to csv df for comparison"""

    scraped_articles_df["url"] = scraped_articles_df["url"].apply(lambda url: url.strip())

    scraped_articles_df["author"] = scraped_articles_df["author"].apply(lambda author: str(author))
    scraped_articles_df["author"] = scraped_articles_df["author"].apply(format_authors)

    return scraped_articles_df


def transform_data() -> None:
    """Combines all functions from transform.py to transform data in one function"""

    scraped_data =get_scraped_data_as_df(SCRAPED_DATA_FOR_COMPARISON)

    scraped_data = format_scraped_articles_df(scraped_data)

    scraped_data.to_csv("transformed_data.csv")


if __name__ == "__main__":

    transform_data()
