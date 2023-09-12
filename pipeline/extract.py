"""Main extract file"""
import requests
import feedparser
from feedparser.util import FeedParserDict
from bs4 import BeautifulSoup as bs
import pandas as pd
import re

RSS_FEED = "https://feeds.bbci.co.uk/news/rss.xml?edition=uk#"
SCRAPED_ARTICLES = "scraped_articles.csv"
RSS_FEED_CSV = "rss_feed.csv"


def read_feed(feed: str):
    """Reads RSS feed"""
    parsed_feed = feedparser.parse(feed)
    return parsed_feed


def transform_to_pandas(feed: FeedParserDict) -> pd.DataFrame:
    """Converts RSS feed list of articles into a pandas dataframe"""
    return pd.DataFrame(feed.entries)


def extract_urls(feed: FeedParserDict) -> list:
    """Extracts URLS from RSS feed"""
    return [entry["id"] for entry in feed.entries]


def scrape_article(article_url: str) -> dict:
    """For a given url, scrape relevant data using BS4, return as a dict"""
    article_dict = {}

    article = requests.get(article_url, timeout=10)
    soup = bs(article.content, 'lxml')
    body = soup.find('main', id='main-content')
    headline = soup.find('h1').text
    if body is not None:
        relevant_divs = body.findAll('div', attrs={"data-component": "text-block"})
        text = " ".join(div.find('p').text for div in relevant_divs)
        author = body.find('div', attrs= {"class": re.compile(".*TextContributorName")})
    else:
        body = soup.find('article')
        if body:
            text = " ".join([p.text for p in body.findAll('p')])
            author = body.find('div', attrs= {"class": re.compile(".*TextContributorName")})


    article_dict["body"] = text
    article_dict["headline"] = headline
    article_dict["url"] = article_url
    article_dict["author"] = getattr(author, "text", None)

    return article_dict


def scrape_all_articles(urls: list) -> pd.DataFrame:
    """Scrapes article data from a list of URLs and returns a dataframe"""
    article_list = []
    for url in urls:
        try:
            article = scrape_article(url)
            if article["headline"] and article["body"]:
                article_list.append(article)
            else:
                continue
        except KeyboardInterrupt:
            raise KeyboardInterrupt("Stopped by user")
        except Exception as exc:
            print(exc)
    return pd.DataFrame(article_list)


def extract_data() -> None:
    """Whole extract process"""
    rss_feed = read_feed(RSS_FEED)
    rss_df = transform_to_pandas(rss_feed)

    article_urls = extract_urls(rss_feed)
    articles = scrape_all_articles(article_urls)

    articles.to_csv(SCRAPED_ARTICLES, index=False)
    rss_df.to_csv(RSS_FEED_CSV, index=False)

if __name__ == "__main__":

    rss_feed = read_feed(RSS_FEED)
    rss_df = transform_to_pandas(rss_feed)

    article_urls = extract_urls(rss_feed)
    articles = scrape_all_articles(article_urls)

    articles.to_csv(SCRAPED_ARTICLES, index=False)
    rss_df.to_csv(RSS_FEED_CSV, index=False)
