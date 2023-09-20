"""Comparison file to compare scraped data with data in the db"""
# pylint: disable=invalid-name
import pandas as pd


TRANSFORMED_ARTICLES_FOR_ARTICLE_VERSION = "transformed_data_for_a_v.csv"
ARTICLES_FOR_COMPARISON = "articles_for_comparison.csv"
ARTICLES_FROM_DB = "previous_versions.csv"
SCRAPED_ARTICLES = "scraped_articles.csv"


def identify_changes(scraped_df: pd.DataFrame, rds_df: pd.DataFrame) -> pd.DataFrame:
    """Identifies changes in the scraped df and returns a df with the article changes"""

    differences = rds_df.merge(scraped_df, how="left", on="article_url")

    differences = differences[(differences["body_x"] != differences["body_y"]) |\
                (differences["heading_x"] != differences["heading_y"])]

    return differences


def split_changes(differences: pd.DataFrame) -> pd.DataFrame:
    """Split the changes in dataframe by body or heading or both"""

    heading_change = differences[(differences["body_x"] == differences["body_y"]) &\
                (differences["heading_x"] != differences["heading_y"])].copy()
    body_change = differences[(differences["body_x"] != differences["body_y"]) &\
                (differences["heading_x"] == differences["heading_y"])].copy()

    double_change = differences[(differences["body_x"] != differences["body_y"]) &\
                (differences["heading_x"] != differences["heading_y"])].copy()

    split_heading_change = double_change[(double_change["body_x"] != double_change["body_y"]) &\
                (double_change["heading_x"] != double_change["heading_y"])].copy()
    split_body_change = double_change[(double_change["body_x"] != double_change["body_y"]) &\
                (double_change["heading_x"] != double_change["heading_y"])].copy()

    heading_change = pd.concat([heading_change, split_heading_change])
    body_change = pd.concat([body_change, split_body_change])

    return heading_change, body_change


def format_changes_comparison(df: pd.DataFrame, type_of_change: str, other_change_column: str) -> pd.DataFrame:
    """Formats the dataframe according to the desired change."""
    df = df.copy()

    df = df.drop(columns=[other_change_column + "_x", other_change_column + "_y"])
    df["change_type"] = type_of_change
    df.columns = ["previous", "article_url", "article_id", "previous_scraped", "current",\
                  "current_scraped", "change_type"]
    df = df.reindex(columns=["article_id", "article_url", "change_type", "previous", "current", \
                            "previous_scraped", "current_scraped"])

    return df


def format_both_changes(heading_df: pd.DataFrame, body_df: pd.DataFrame) -> pd.DataFrame:
    """Formats both heading and body changes into one df"""

    heading_change = format_changes_comparison(heading_df, "heading", "body")
    body_change = format_changes_comparison(body_df, "body", "heading")

    return pd.concat([heading_change, body_change])


def format_changes_version(df: pd.DataFrame) -> pd.DataFrame:
    """Formats the dataframe to fit the article_version table."""

    df = df.drop(columns=["body_x", "heading_x", "scraped_at_x", "article_url"]).copy()
    df.columns = ["article_id", "body", "heading", "scraped_at"]

    df = df.reindex(columns=["scraped_at", "heading", "body", "article_id"])
    return df


def transform_data() -> None:
    """Compares scraped data with the data in the db and identifies where there are difference"""

    try:
        scraped_data = pd.read_csv(SCRAPED_ARTICLES)
        previous_versions = pd.read_csv(ARTICLES_FROM_DB)
        comparison_df = pd.DataFrame()
        version_df = pd.DataFrame()

        differences = identify_changes(scraped_data, previous_versions)
        if not differences.empty:
            heading_change, body_change = split_changes(differences)
            comparison_df = format_both_changes(heading_change, body_change)
            version_df = format_changes_version(pd.concat([heading_change, body_change]))

        comparison_df.to_csv(ARTICLES_FOR_COMPARISON, index=False)
        version_df.to_csv(TRANSFORMED_ARTICLES_FOR_ARTICLE_VERSION, index=False)
    except KeyboardInterrupt:
        print("User stopped.")
    except pd.errors.EmptyDataError:
        print("No changes at this time")
    except Exception as exc:
        print(exc)


if __name__ == "__main__":

    transform_data()
