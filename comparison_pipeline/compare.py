"""Comparison file to compare scraped data with data in the db"""

import pandas as pd
from psycopg2.extensions import connection

from extract import get_db_connection


SCRAPED_DATA_TRANSFORMED = "transformed_data.csv"


def get_scraped_data_as_df(file_path: str) -> pd.DataFrame:
    """Returns scraped data from extract"""

    return pd.read_csv(file_path)


#TODO Remove test schema selection from function
def get_latest_version_of_article_from_db(conn: connection) -> pd.DataFrame:
    """Returns data from rds database in a dataframe for comparison"""

    cur = conn.cursor()

    cur.execute("""SELECT 
                test.article.article_id, test.article.article_url,
                test.article_version.heading, test.article_version.body,
                test.article_version.scraped_at,
                string_agg(test.author.author_name, ',') AS author_name
                FROM test.article
                LEFT JOIN test.article_version
                ON test.article_version.article_id = test.article.article_id
                LEFT JOIN test.article_author
                ON test.article_author.article_id = test.article.article_id
                LEFT JOIN test.author
                ON test.article_author.author_id = test.author.author_id
                WHERE test.article_version.scraped_at = (SELECT MAX(test.article_version.scraped_at) 
                FROM test.article_version WHERE test.article.article_id = test.article_version.article_id)
                GROUP BY test.article.article_id, test.article.article_url, 
                test.article_version.heading, test.article_version.body,
                scraped_at
                ;""")

    data = cur.fetchall()

    return pd.DataFrame(data, 
                        columns=["article_id","article_url", "heading",
                                 "body", "scraped_at", "author_name"])


def split_author_name_row(row: str | None) -> list[str] | None:
    """splits author row into common structure type for comparison"""

    if not isinstance(row, str):
        return 
    
    row = row.split(",")
    row.sort()
    
    return row


def identify_changes(scraped_df: pd.DataFrame, rds_df: pd.DataFrame) -> pd.DataFrame:
    """Identifies the changes in the scraped df and returns a df with the articles that have changes"""
    
    joined_df = pd.merge(left=scraped_df, right=rds_df, left_on=["url"], right_on=["article_url"])

    differences_in_body = joined_df[joined_df["body_x"] != joined_df["body_y"]].copy()
    differences_in_body = differences_in_body[["article_id", "body_y"]]

    differences_in_headline = joined_df[joined_df["heading"] != joined_df["headline"]].copy()
    differences_in_headline = joined_df[["article_id", "heading"]]

    joined_df["author_name"] = joined_df["author_name"].apply(split_author_name_row)
    differences_in_authors = joined_df[joined_df["author"] != joined_df["author_name"]].copy()
    differences_in_authors = joined_df[["article_id", "author_name"]]

    difference_in_articles = pd.merge(differences_in_body, differences_in_headline, "outer", ["article_id"])
    difference_in_articles = pd.merge(difference_in_articles, differences_in_authors, "outer", ["article_id"])

    return difference_in_articles


def compare_data() -> None:
    """Compares scraped data with the data in the db and identifies where there are difference"""

    conn = get_db_connection()

    scraped_data_transformed_df = get_scraped_data_as_df(SCRAPED_DATA_TRANSFORMED)

    article_data_in_db_df = get_latest_version_of_article_from_db(conn)

    changes_in_article_df = identify_changes(scraped_data_transformed_df,
                                             article_data_in_db_df)
    
    print(changes_in_article_df)
    
    #TODO Append changes as a new entry in db
    #TODO 
    #TODO Update scraped at timings for entries in the db that exist 

    conn.close()


if __name__ == "__main__":

    compare_data()
