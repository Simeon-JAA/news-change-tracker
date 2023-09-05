"""Pytest fixtures file"""
import pytest

@pytest.fixture
def rss_feed():
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
    return {"body" : "text",
            "headline" : "headline",
            "url" : "fakeurl.com",
            "author" : "scoobert doobert"}


@pytest.fixture
def bbc_sport_dict():
    return {"body" : "text",
            "headline" : "headline",
            "url" : "fakeurl.com",
            "author" : None}

@pytest.fixture
def bbc_sport_html():
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