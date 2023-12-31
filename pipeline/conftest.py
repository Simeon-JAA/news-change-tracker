"""Pytest fixtures file"""
import pytest
import pandas as pd

@pytest.fixture
def rss_feed():
    """rss feed dictionary fixture"""
    return {
        "entries" : [
            {
            "title" : "article title",
            "summary" : "article summary"
            }
        ]
    }

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
            "headline" : "headline",
            "url" : "fakeurl.com",
            "author" : "scoobert doobert"}


@pytest.fixture
def bbc_sport_dict():
    """bbc sport article returned dict fixture"""
    return {"body" : "text",
            "headline" : "headline",
            "url" : "fakeurl.com",
            "author" : None}

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
def mock_dataframe():
    """Fixture for raw dataframe"""
    return pd.DataFrame([{
        "id": "https://www.bbc.co.uk/news/uk-politics-66707569	",
        "published": "Mon, 04 Sep 2023 12:02:28 GMT",
        "title": "Angela Rayner handed new role"
    }])

@pytest.fixture
def mock_scraped_df():
    """Fixture for scraped article dataframe"""
    return pd.DataFrame([{
        "author" : "By Scooby & Shaggy and Scrappy",
        "headline" : "headline1",
        "url" : "www.realurl.com ",
        "body" : "body1"},
        {
        "author" : "NaN",
        "headline" : "headline2",
        "url" : " www.realurl.com",
        "body" : "body2"
        }])


@pytest.fixture
def mock_loading_df():
    """Fixture for mock df to be used in testing load"""
    return pd.DataFrame([{
        "title" : "title",
        "url" : "www.test.com",
        "headline" : "headline",
        "body" : "body",
        "author" : "Miss Chanandler Bong",
        "published" : "2023-09-07 14:05:53+01:00",
    }])
