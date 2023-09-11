"""Main file for analysis on modified articles"""

from rapidfuzz.fuzz import ratio
import pandas as pd
from difflib import unified_diff

ARTICLES_FOR_COMPARISON = "articles_for_comparison.csv"


def similarity(previous_version: str, current_version: str) -> float:
    """Fuzzy matches the two versions. Returns a ratio"""

    result = ratio(previous_version, current_version)

    return result


def find_differences(df: pd.DataFrame) -> None:
    """Splits the different versions by their similarities and differences"""

    txt = "I like tomatoes and fruits jcgjcgcjgjcg".split()

    txt2 = "I don't know if I like or not like tomatoes and fruits".split()

    print('\n'.join(list(unified_diff(txt, txt2))))
# highlight everything thats a plus in the new, highlight minus in the og


def compare_data() -> None:
    """Implores fuzzy matching to compare the two changes side by side"""

    article_changes = pd.read_csv(ARTICLES_FOR_COMPARISON)

    if not article_changes.empty:
        article_changes["proportion_changed"] = article_changes.apply(lambda row:\
                similarity(row["previous"], row["current"]), axis=1)
        find_differences(article_changes)


if __name__ == "__main__":
    compare_data()
