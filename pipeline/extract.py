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
    try:
        body = soup.find('main', id='main-content')
        headline = soup.find('h1').text
        relevant_divs = body.findAll('div', attrs={"data-component": "text-block"})
        for div in relevant_divs:
            print(div.find('p').text)
        
        text = " ".join([p.text for p in body.findAll('p')])
        
        article_dict["body"] = (text)
        article_dict["headline"] = headline

    # BBC sport scraping - separate func?
    except:
    
        body = soup.find('article')
        headline = soup.find('h1').text
        text = " ".join([p.text for p in body.findAll('p')])

        article_dict["body"] = (text)
        article_dict["headline"] = headline

    return article_dict


if __name__ == "__main__":
    feed = read_feed(RSS_FEED)
    
    urls = extract_urls(feed)
    url = 'https://www.bbc.co.uk/news/uk-66531409?at_medium=RSS&at_campaign=KARANGA'
    scrape_article(url)
   
    # articles = []
    # for url in urls:
    #     try:
    #         print(url)
    #         article = scrape_article(url)
    #         print(article["headline"])
    #         if article["headline"]:
    #             articles.append(article)
    #     except:
    #         continue
    

