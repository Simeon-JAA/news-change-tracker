"""Transforms the data by flattening and cleaning before it goes into the load stage"""

from datetime import datetime

import pandas as pd
import pytz
from pandas import DataFrame

RSS_FEED_DATA = "rss_feed.csv"
SCRAPED_DATA = "scraped_articles.csv"
TRANSFORMED_DATA_CSV = "transformed_data.csv"


def get_rss_feed_df(file_path: str) -> DataFrame:
    """Returns the scraped article csv as a DataFrame"""

    rss_df = pd.read_csv(file_path)

    return rss_df


def get_scraped_articles_df(file_path: str) -> DataFrame:
    """Returns the rss_feed csv as a DataFrame"""

    scraped_article_df = pd.read_csv(file_path)

    return scraped_article_df


def format_time_to_timestamp(time_in_col: str) -> datetime:
    """Formats time to timestamp format to load into postgres"""

    time_in_col = time_in_col[5:]
    gmt = pytz.timezone("Europe/London")
    time_in_col = gmt.localize(datetime.strptime(time_in_col, "%d %b %Y %H:%M:%S %Z"))

    return time_in_col


def format_rss_feed_df(rss_df: DataFrame) -> DataFrame:
    """Formats rss feed dataframe columns before saving to csv df"""

    rss_df["published"] = rss_df["published"].apply(format_time_to_timestamp)
    rss_df["id"] = rss_df["id"].apply(lambda url: url.strip())
    rss_df = rss_df[["id", "title", "published"]]

    return rss_df


def format_authors(authors: str) -> str | None :
    """Returns a list of authors if they exist, and none if they dont"""

    if authors.lower() == "nan":
        return None

    if authors[:3].lower() == "by ":
        authors = authors.lower().replace("by ", "", 1)
    authors = authors.replace(" &", ",")
    authors = authors.replace(" and", ",")
    authors = authors.split(", ")

    authors = list(map(lambda author: author.title(), authors))
    
    return authors


def format_scraped_articles_df(scraped_articles_df: DataFrame) -> DataFrame:
    """Formats scraped_articles dataframe columns before saving to csv df"""

    scraped_articles_df["url"] = scraped_articles_df["url"].apply(lambda url: url.strip())

    scraped_articles_df["author"] = scraped_articles_df["author"].apply(lambda authors:
                                                                        str(authors))
    scraped_articles_df["author"] = scraped_articles_df["author"].apply(format_authors)

    return scraped_articles_df


def transform_data() -> None:
    """Whole process of transforming data"""

    rss_feed_df = get_rss_feed_df("rss_feed.csv")

    rss_feed_df = format_rss_feed_df(rss_feed_df)

    scraped_article_df = get_scraped_articles_df("scraped_articles.csv")

    scraped_article_df = format_scraped_articles_df(scraped_article_df)

    joined_data = pd.merge(left=scraped_article_df,
                            right=rss_feed_df,
                            left_on="url",
                            right_on="id",
                            how="inner")

    joined_data = joined_data[["title", "url", "headline", "body", "author", "published"]]

    joined_data.to_csv(TRANSFORMED_DATA_CSV)


if __name__ == "__main__":

    rss_feed_df = get_rss_feed_df(RSS_FEED_DATA)

    rss_feed_df = format_rss_feed_df(rss_feed_df)

    articles_df = get_scraped_articles_df(SCRAPED_DATA)

    articles_df = format_scraped_articles_df(articles_df)

    joined_data = pd.merge(left=articles_df,
                            right=rss_feed_df,
                            left_on="url",
                            right_on="id",
                            how="inner")

    joined_data = joined_data[["title", "url", "headline", "body", "author", "published"]]

    joined_data.to_csv(TRANSFORMED_DATA_CSV)