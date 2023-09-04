"""Main extract file"""
import requests
import feedparser
from feedparser.util import FeedParserDict
from bs4 import BeautifulSoup as bs
import pandas as pd

RSS_FEED = "https://feeds.bbci.co.uk/news/rss.xml?edition=uk#"


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


def scrape_article(article_url: str)->dict:
    """For a given url, scrape relevant data using BS4, return as a dict"""
    article_dict = {}
    
    article = requests.get(article_url)
    soup = bs(article.content, 'lxml')
    body = soup.find('main', id='main-content')
    headline = soup.find('h1').text
    if body is not None:
        relevant_divs = body.findAll('div', attrs={"data-component": "text-block"})
        text = " ".join(div.find('p').text for div in relevant_divs)
    else:    
        body = soup.find('article')
        if body:
            text = " ".join([p.text for p in body.findAll('p')])

    article_dict["body"] = text
    article_dict["headline"] = headline
    article_dict["url"] = article_url

    return article_dict


def scrape_all_articles(urls:list)->pd.DataFrame:
    """Scrapes article data from a list of URLs and returns a dataframe"""
    articles = []
    for url in urls:
        try:
            article = scrape_article(url)
            if article["headline"] and article["body"]:
                articles.append(article)
            else: 
                continue
        except:
            continue
    return pd.DataFrame(articles)

if __name__ == "__main__":
    feed = read_feed(RSS_FEED)
    rss_df = transform_to_pandas(feed)
    print(rss_df)
    
    urls = extract_urls(feed)
    # url = 'https://www.bbc.co.uk/sport/football/66703473'
    # print(scrape_article(url))
   
    articles = scrape_all_articles(urls)
    print(articles)
    
    articles.to_csv("scraped_articles.csv", index=False)
    rss_df.to_csv("rss_feed.csv", index=False)
    

