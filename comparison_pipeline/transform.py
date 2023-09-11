"""Comparison file to compare scraped data with data in the db"""
# pylint: disable=invalid-name
import pandas as pd
from psycopg2.extensions import connection
from extract import get_db_connection


TRANSFORMED_ARTICLES_FOR_ARTICLE_VERSION = "transformed_data_for_a_v.csv"
ARTICLES_FOR_COMPARISON = "articles_for_comparison.csv"
ARTICLES_FROM_DB = "previous_versions.csv"
SCRAPED_ARTICLES = "scraped_articles.csv"


def identify_changes(scraped_df: pd.DataFrame, rds_df: pd.DataFrame) -> pd.DataFrame:
    """Identifies changes in the scraped df and returns a df with the article changes"""

    differences = scraped_df.compare(rds_df.drop(columns=["article_id"]), \
                            result_names=("updated", "previous"), keep_equal=True, keep_shape=True)


    differences = differences[(differences["heading"]["updated"] != \
                                differences["heading"]["previous"])
                    | (differences["body"]["updated"] != differences["body"]["previous"])]
    differences = differences.drop(columns=[("article_url", "previous")])

    return differences


def format_comparison(df: pd.DataFrame, conn: connection) -> pd.DataFrame:
    """Prepares the differences dataframe for further analysis.
    Returns a dataframe"""

    headline_changes = changes_to_article(df, "heading", "body")

    body_changes = changes_to_article(df, "body", "heading")

    both_changes = double_change_to_article(df)

    all_changes = pd.concat([headline_changes, body_changes, both_changes])

    if not all_changes.empty:
        all_changes["article_id"] = all_changes["article_url"].apply(lambda x: \
                                    retrieve_article_id(conn, x))
        all_changes = all_changes.reindex(columns=["article_id", "article_url", \
        "type_of_change", "previous", "current", "previous_scraped_at", "current_scraped_at"])

    return all_changes


def changes_to_article(df: pd.DataFrame, type_of_change: str, removing: str) -> pd.DataFrame:
    """Keeps only desired type of change done to the articles. Returns formatted df"""

    changes = df[df[removing]["previous"] == df[removing]["updated"]].copy()
    if not changes.empty:
        changes = changes.drop(columns=[removing])
        changes["type_of_change"] = type_of_change
        changes.columns = ["current", "previous", "article_url", \
                    "current_scraped_at", "previous_scraped_at", "type_of_change"]

    return changes


def double_change_to_article(df: pd.DataFrame) -> pd.DataFrame:
    """Refactors dataframe to reflect changes done to both body and headline from same
    scraping. Returns formatted df"""

    changes = df[(df["heading"]["previous"] != df["heading"]["updated"]) & \
                      (df["body"]["previous"] != df["body"]["updated"])]
    if not changes.empty:
        heading_changes = changes.copy().drop(columns=["body"])
        heading_changes["type_of_change"] = "heading"
        heading_changes.columns = ["current", "previous", "article_url", \
                    "current_scraped_at", "previous_scraped_at", "type_of_change"]

        body_changes = changes.copy().drop(columns=["heading"])
        body_changes["type_of_change"] = "body"
        body_changes.columns = ["current", "previous", "article_url", \
                    "current_scraped_at", "previous_scraped_at", "type_of_change"]

        changes = pd.concat([heading_changes, body_changes])
    return changes


def format_article_version_update(df: pd.DataFrame, conn: connection) -> pd.DataFrame:
    """Prepares the differences dataframe to fit for the article_version table in RDS.
    Returns a dataframe"""
    df = df.copy()
    df = df.drop(columns=[("heading","previous"),\
                                ("body","previous"),("scraped_at","previous")])
    df.columns = ["body", "heading", "article_url", "scraped_at"]
    df["article_id"] = df["article_url"].apply(lambda x: retrieve_article_id(conn, x))
    df.drop(columns=["article_url"], inplace=True)
    df = df.reindex(columns=["scraped_at", "heading", "body", "article_id"])

    return df


def retrieve_article_id(conn: connection, url: str) -> str:
    """Retrieves article_id from the RDS by using the url"""

    with conn.cursor() as cur:
        cur.execute("""SELECT article_id FROM article WHERE article_url = %s""", [url])
        article_id = cur.fetchone()[0]
        return article_id


def transform_data() -> None:
    """Compares scraped data with the data in the db and identifies where there are difference"""

    try:
        db_conn = get_db_connection()

        scraped_data = pd.read_csv(SCRAPED_ARTICLES)
        previous_versions = pd.read_csv(ARTICLES_FROM_DB)

        if not scraped_data.empty and not previous_versions.empty:
            differences = identify_changes(scraped_data, previous_versions)
            df_for_article_version = pd.DataFrame()
            df_for_comparison = pd.DataFrame()

            if not differences.empty:
                df_for_article_version = format_article_version_update(differences, db_conn)
                df_for_comparison = format_comparison(differences, db_conn)

            df_for_article_version.to_csv(TRANSFORMED_ARTICLES_FOR_ARTICLE_VERSION, index=False)
            df_for_comparison.to_csv(ARTICLES_FOR_COMPARISON, index=False)
    except KeyboardInterrupt:
        raise KeyboardInterrupt("Stopped by user")
    except Exception as exc:
        print(exc)
    finally:
        db_conn.close()


if __name__ == "__main__":

    transform_data()
