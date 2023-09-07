"""Extraction file for comparison pipeline"""

from os import environ
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv
from psycopg2 import connect, OperationalError
from psycopg2.extensions import connection


SCRAPED_ARTICLES_FOR_COMPARISON = "scraped_articles_for_comparison.csv"


def get_db_connection() -> connection:
    """Returns connection to the rds database"""

    load_dotenv()

    try:
        return connect(host=environ["DB_HOST"],
                   user=environ["DB_USER"],
                   password=environ["DB_PASSWORD"],
                   port=environ["DB_PORT"],
                   dbname=environ["DB_NAME"])
    except Exception as exc:
        print(f"get_db_connection Error: {exc}")
        raise Exception()


def get_urls_from_article_table(conn: connection)-> list[str]:
    """Connects to the database and returns selected columns of selected table as a list"""

    with conn.cursor() as cur:
        try:
            cur.execute("SELECT article_url FROM test.article;")
            result = cur.fetchall()
            result = [url[0] for url in result]
        except (ConnectionError, OperationalError) as err:
            err("Error: Unable to retrieve data from database")

    return result


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


def scrape_all_articles(list_of_urls: list[str]) -> pd.DataFrame:
    """Scrapes article data from a list of URLs and returns a dataframe"""

    article_list = []

    for url in list_of_urls:
        try:
            article = scrape_article(url)
        except KeyboardInterrupt:
            raise KeyboardInterrupt("Stopped by user")
        except Exception as exc:
            print(exc)

        article_list.append(article)

    return pd.DataFrame(article_list)


def extract_data() -> None:
    """Contains all functions in extract.py to fulfil whole extract process"""

    conn = get_db_connection()

    url_list = get_urls_from_article_table(conn)

    scraped_article_information = scrape_all_articles(url_list)

    scraped_article_information.to_csv(SCRAPED_ARTICLES_FOR_COMPARISON, index=False)

    conn.close()


if __name__ == "__main__":

    conn = get_db_connection()

    url_list = get_urls_from_article_table(conn)

    scraped_article_information = scrape_all_articles(url_list)

    scraped_article_information.to_csv(SCRAPED_ARTICLES_FOR_COMPARISON, index=False)

    conn.close()
