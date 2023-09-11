"""Main file for analysis on modified articles"""

from rapidfuzz.fuzz import partial_ratio
import pandas as pd

ARTICLES_FOR_COMPARISON = "articles_for_comparison.csv"


def fuzzy_match(previous_version: str, current_version: str) -> float:
    """Fuzzy matches the two versions. Returns a partial ratio"""

    result = partial_ratio(previous_version, current_version)

    return result



def compare_data() -> None:
    """Implores fuzzy matching to compare the two changes side by side"""

    article_changes = pd.read_csv(ARTICLES_FOR_COMPARISON)

    if not article_changes.empty:
        article_changes["c"]


if __name__ == "__main__":
    pass
