"""Main extract file"""
import requests
import feedparser
from feedparser.util import FeedParserDict
# from bs4 import BeautifulSoup as bs
import pandas as pd
# import urllib.request

RSS_FEED = "https://feeds.bbci.co.uk/news/rss.xml?edition=uk#"


def read_feed(feed: str):
    """Reads RSS feed"""
    parsed_feed = feedparser.parse(feed)
    return parsed_feed


def transform_to_pandas(feed: FeedParserDict) -> pd.DataFrame:
    """Converts RSS feed list of articles into a pandas dataframe"""
    return pd.DataFrame(feed.entries)


# def url_list_to_html(df: pd.DataFrame) -> list:
#     """Extract urls from dataframe for parsing"""

#     return [entry.id for entry in df.itertuples()]

if __name__ == "__main__":
    feed = read_feed(RSS_FEED)

    df = transform_to_pandas(feed)
    pd.set_option('display.max_columns', None)
    print(df)
    df.to_csv("extract_file.csv")


