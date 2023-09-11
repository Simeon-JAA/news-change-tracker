"""Extraction file for comparison pipeline"""

from os import environ
import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv
from psycopg2 import connect, OperationalError
from psycopg2.extensions import connection

ARTICLES_FROM_DB = "previous_versions.csv"
SCRAPED_ARTICLES = "scraped_articles.csv"
TIME_NOW = datetime.datetime.now().replace(microsecond=0)


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


def get_urls_from_article_table(conn: connection) -> list:
    """Connects to the database and returns selected columns of selected table as a list"""

    with conn.cursor() as cur:
        try:
            cur.execute("SELECT article_url FROM article;")
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
        relevant_divs = body.findAll(
            'div', attrs={"data-component": "text-block"})
        text = " ".join(div.find('p').text for div in relevant_divs)
    else:
        body = soup.find('article')
        if body:
            text = " ".join([p.text for p in body.findAll('p')])

    article_dict["body"] = text
    article_dict["heading"] = headline
    article_dict["article_url"] = article_url
    article_dict["scraped_at"] = TIME_NOW

    return article_dict


def scrape_all_articles(urls: list) -> pd.DataFrame:
    """Scrapes article data from a list of URLs and returns a dataframe"""
    article_list = []

    for url in urls:
        article = scrape_article(url)
        if article["heading"] and article["body"]:
            article_list.append(article)

    return pd.DataFrame(article_list)


def get_latest_version_of_article_from_db(conn: connection) -> pd.DataFrame:
    """Returns data from rds database in a dataframe for comparison"""

    with conn.cursor() as cur:

        cur.execute("""SELECT article_version.body,
                article_version.heading, article.article_url,
                article.article_id,
                article_version.scraped_at
                FROM article
                LEFT JOIN article_version
                ON article_version.article_id = article.article_id
                WHERE article_version.scraped_at = (SELECT MAX(article_version.scraped_at)
                FROM article_version WHERE article.article_id = article_version.article_id)
                GROUP BY article.article_id, article.article_url,
                article_version.heading, article_version.body,
                scraped_at
                ;""")

        data = cur.fetchall()

    return pd.DataFrame(data,
                        columns=["body", "heading", "article_url", "article_id",
                                 "scraped_at"])


def extract_data() -> None:
    """Contains all functions in extract.py to fulfil whole extract process"""

    try:
        db_conn = get_db_connection()

        url_list = get_urls_from_article_table(db_conn)
        scraped_article_information = pd.DataFrame()
        previous_versions = pd.DataFrame()
        if len(url_list) > 0:
            scraped_article_information = scrape_all_articles(url_list)
            previous_versions = get_latest_version_of_article_from_db(db_conn)

            scraped_article_information.to_csv(SCRAPED_ARTICLES, index=False)
            previous_versions.to_csv(ARTICLES_FROM_DB, index=False)
    except KeyboardInterrupt:
        raise KeyboardInterrupt("Stopped by user")
    except Exception as exc:
        print(exc)
    finally:
        db_conn.close()


if __name__ == "__main__":

    extract_data()
