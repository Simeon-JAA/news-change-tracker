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

    cur.execute("""SELECT test.article.article_id, test.article.source,
                test.article.article_url, test.article_version.heading,
                test.article_version.body, test.article_version.scraped_at,
                test.author.author_name, test.author.author_id
                FROM test.article
                LEFT JOIN test.article_version
                ON test.article_version.article_id = test.article.article_id
                LEFT JOIN test.article_author
                ON test.article_author.article_id = test.article.article_id
                LEFT JOIN test.author
                ON test.article_author.author_id = test.author.author_id
                WHERE test.article_version.scraped_at = (SELECT MAX(test.article_version.scraped_at) 
                FROM test.article_version WHERE test.article.article_id = test.article_version.article_id)
                ;""")

    data = cur.fetchall()

    return pd.DataFrame(data, 
                        columns=["article_id", "source",
                                 "article_url", "heading", "body",
                                 "scraped_at", "author_name", "author_id"])


def identify_changes(scraped_df: pd.DataFrame, rds_df: pd.DataFrame) -> pd.DataFrame:
    """Identifies the changes in the scraped df and returns a df with the articles that have changes"""
    
    joined_df = pd.merge(left=scraped_df, right=rds_df, left_on=["url"], right_on=["article_url"])

    differences_in_body = joined_df[joined_df["body_x"] != joined_df["body_y"]]
    differences_in_body = differences_in_body[["article_id", "body_x", "body_y"]]
    print(differences_in_body)

    differences_in_headline = joined_df[joined_df["heading"] != joined_df["headline"]]
    differences_in_headline = joined_df[["article_id", "headline", "heading"]]
    print(differences_in_headline)

    # differences_in_author = joined_df[joined_df["author_x"] not in joined_df["author_y"]]

    return joined_df


def compare_data() -> None:
    """Compares scraped data with the data in the db and identifies where there are difference"""

    conn = get_db_connection()

    scraped_data_transformed_df = get_scraped_data_as_df(SCRAPED_DATA_TRANSFORMED)

    article_data_in_db_df = get_latest_version_of_article_from_db(conn)

    # print(article_data_in_db_df)
    # print(scraped_data_transformed_df.columns)
    # print(scraped_data_transformed_df[["headline", "body"]])
    # print(article_data_in_db_df[[ "heading", "body"]])

    #TODO Recognise changes and append to new file
    identify_changes(scraped_data_transformed_df, article_data_in_db_df)
    #TODO Append changes as a new entry in db
    #TODO 
    #TODO Update scraped at timings for entries in the db that exist 

    conn.close()


if __name__ == "__main__":

    compare_data()
