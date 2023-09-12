"""Main file for analysis on modified articles"""

from difflib import unified_diff
from rapidfuzz.fuzz import ratio
import pandas as pd

ARTICLES_FOR_COMPARISON = "articles_for_comparison.csv"
TRANSFORMED_ARTICLES_FOR_ARTICLE_CHANGE = "transformed_data_for_a_c.csv"


def similarity(previous_version: str, current_version: str) -> float:
    """Fuzzy matches the two versions. Returns a ratio"""

    result = ratio(previous_version, current_version)

    return result


def adjust_for_change(symbol: str, differences: list) -> str:
    """Adjusts the entry to reflect either the original with details removed,
    or the update with added details"""

    new_differences = []

    for word in differences:
        # A symbol that wouldn't be used in traditional media
        if '@@' in word:
            new_differences.append("£$")
        elif not word[0] == symbol:
            new_differences.append(word)
    # another symbol that wouldn't be used in traditional media
    return "§%".join(new_differences)


def compare_data() -> None:
    """Implores fuzzy matching to compare the two changes side by side"""

    try:
        article_changes = pd.read_csv(ARTICLES_FOR_COMPARISON)

        article_changes["similarity"] = article_changes.apply(lambda row:\
                    similarity(row["previous"], row["current"]), axis=1)

            # finds the differences between changed parts
        article_changes["differences"] = article_changes.apply(lambda row:\
    list(unified_diff(row["previous"].split(), row["current"].split()))[2:], axis=1)
        article_changes["current"] = article_changes["differences"].apply(\
            lambda x: adjust_for_change("-", x))
        article_changes["previous"] = article_changes["differences"].apply(\
            lambda x: adjust_for_change("+", x))
        # format the columns
        article_changes.drop(columns=["differences"], inplace=True)
        article_changes["similarity"] = article_changes["similarity"].round(2)
        article_changes.to_csv(TRANSFORMED_ARTICLES_FOR_ARTICLE_CHANGE, index=False)
    except KeyboardInterrupt:
        print("User stopped.")
    except pd.errors.EmptyDataError:
        print("No changes at this time")


if __name__ == "__main__":
    compare_data()
