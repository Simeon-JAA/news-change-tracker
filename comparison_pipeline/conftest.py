"""Pytest fixtures file"""
import pytest
import pandas as pd

@pytest.fixture
def bbc_html():
    """bbc example html fixture"""
    html = "<html>" \
            "<body>" \
                "<main id=\"main-content\">" \
                    "<article>" \
                        "<header>" \
                            "<h1>" \
                                "headline" \
                            "</h1>" \
                        "</header>" \
                        "<div class= \"TextContributorName\">" \
                            "scoobert doobert" \
                        "</div>" \
                        "<div data-component=\"text-block\">" \
                            "<p>" \
                                "text" \
                            "</p>" \
                        "</div>" \
                    "</article>" \
                "</main>" \
            "</body>" \
        "</html>"

    return html

@pytest.fixture
def bbc_article_dict():
    """bbc article returned dict fixture"""
    return {"body" : "text",
            "heading" : "headline",
            "article_url" : "www.fakeurl.com"
            "scraped_at" "fake time",
            }


@pytest.fixture
def bbc_sport_dict():
    """bbc sport article returned dict fixture"""
    return {"body" : "text",
            "heading" : "headline",
            "article_url" : "www.fakeurl.com"
            "scraped_at" "fake time",
            }

@pytest.fixture
def bbc_sport_html():
    """bbc sport example html fixture"""
    html = "<html>" \
            "<body>" \
                "<article>" \
                    "<header>" \
                        "<h1>" \
                            "headline" \
                        "</h1>" \
                    "</header>" \
                    "<div>" \
                        "<p>" \
                            "text" \
                        "</p>" \
                    "</div>" \
                "</article>" \
            "</body>" \
        "</html>"
    return html


@pytest.fixture
def mock_loading_df():
    """Fixture for mock df to be used in testing load"""
    return pd.DataFrame([{
        "article_url" : "www.test.com",
        "heading" : "headline",
        "body" : "body",
        "scraped_at" : "time",
        "article_id" : "1"
    }]).reset_index(drop=True)


@pytest.fixture
def mock_changed_df():
    """Fixture for mock df to be used in testing transform"""
    return pd.DataFrame([{
        "article_url" : "www.test.com",
        "heading" : "new headline",
        "body" : "body",
        "scraped_at" : "time",
    }]).reset_index(drop=True)


@pytest.fixture
def mock_compared_df():
    """Fixture for mock compared df"""
    cols = pd.MultiIndex.from_product([
        ["heading", "body", "article_url", "scraped_at"],
        ["previous", "updated"]
    ])

    return pd.DataFrame(
    [("headline", "headline", "body", "new body", "url", "new url", "time", "new time")
    ], columns= cols).drop(columns=[("article_url", "previous")])


@pytest.fixture
def mock_compared_double_diff_df():
    """Fixture for mock compared df"""
    cols = pd.MultiIndex.from_product([
        ["heading", "body", "article_url", "scraped_at"],
        ["previous", "updated"]
    ])

    return pd.DataFrame(
    [("headline", "new headline", "body", "new body", "url", "new url", "time", "new time")
    ], columns= cols).drop(columns=[("article_url", "previous")])
