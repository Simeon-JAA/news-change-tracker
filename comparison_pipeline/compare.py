"""Comparison file to compare scraped data with data in the db"""
# pylint: disable=invalid-name
import pandas as pd
from psycopg2.extensions import connection
from extract import get_db_connection


TRANSFORMED_ARTICLES = "transformed_data.csv"
ARTICLES_FROM_DB = "previous_versions.csv"
SCRAPED_ARTICLES = "scraped_articles.csv"


def identify_changes(scraped_df: pd.DataFrame, rds_df: pd.DataFrame) -> pd.DataFrame:
    """Identifies changes in the scraped df and returns a df with the article changes"""

    differences = scraped_df.compare(rds_df.drop(columns=["article_id"]), \
                            result_names=("updated", "previous"), keep_equal=True, keep_shape=True)

    differences = differences[(differences["heading"]["updated"] != differences["heading"]["previous"]) \
                              | (differences["body"]["updated"] != differences["body"]["previous"])]

    differences = differences.drop(columns=[("article_url", "previous"),("heading","previous"),\
                                ("body","previous"),("scraped_at","previous")])
    differences.columns = ["body", "heading", "article_url", "scraped_at"]
    return differences


def retrieve_article_id(conn: connection, url: str) -> str:
    """Retrieves article_id from the RDS by using the url"""

    with conn.cursor() as cur:
        cur.execute("""SELECT article_id FROM article WHERE article_url = %s""", [url])
        article_id = cur.fetchone()[0]
        return article_id


def compare_data() -> None:
    """Compares scraped data with the data in the db and identifies where there are difference"""

    try:
        db_conn = get_db_connection()

        scraped_data = pd.read_csv(SCRAPED_ARTICLES)
        previous_versions = pd.read_csv(ARTICLES_FROM_DB)
        if not scraped_data.empty and not previous_versions.empty:
            differences = identify_changes(scraped_data, previous_versions)
            differences["article_id"] = differences["article_url"].apply\
                (lambda x: retrieve_article_id(db_conn, x))
            differences = differences.reindex(columns=["scraped_at", "heading", "body", \
                                "article_id", "article_url"]).drop(columns=["article_url"])
            differences.to_csv(TRANSFORMED_ARTICLES, index=False)
    except KeyboardInterrupt:
        raise KeyboardInterrupt("Stopped by user")
    except Exception as exc:
        print(exc)
    finally:
        db_conn.close()


if __name__ == "__main__":

    compare_data()