"""Dashboard script"""

from os import environ
from dotenv import load_dotenv
import pandas as pd
from psycopg2 import connect
from psycopg2.extensions import connection
import streamlit as st
import plotly.express as px
from annotated_text import annotated_text
import requests
from bs4 import BeautifulSoup as bs
import re
import altair as alt
import warnings

def get_image(url: str) -> None:
    article = requests.get(url, timeout=10)
    soup = bs(article.content, 'lxml')
    picture = soup.find('img', {"srcset": re.compile(".*")})["src"]
    return picture


def get_db_connection() -> connection:
    """Returns connection to the rds database"""

    load_dotenv()

    return connect(host=environ["DB_HOST"],
                   user=environ["DB_USER"],
                   password=environ["DB_PASSWORD"],
                   port=environ["DB_PORT"],
                   dbname=environ["DB_NAME"])


conn = get_db_connection()


@st.cache_data
def retrieve_article_info() -> pd.DataFrame:
    """Retrieves all article information. Returns dataframe"""

    with conn.cursor() as cur:

        cur.execute("""SELECT ar.article_id, ar.article_url,
                    ar.source FROM article ar;""")

        data = cur.fetchall()

    data = pd.DataFrame(data, columns=["article_id", "article_url",
                                       "source"])

    return data


@st.cache_data
def retrieve_heading(article_id: str) -> str:
    """Retrieves heading for selected articles"""

    with conn.cursor() as cur:
        cur.execute("""SELECT av.heading FROM
                    article_version av JOIN article ar ON av.article_id = ar.article_id WHERE av.article_id = %s ORDER BY scraped_at
                    ASC LIMIT 1;""", [article_id])
        heading = cur.fetchall()[0][0]
        return heading


@st.cache_data
def retrieve_article_changes() -> pd.DataFrame:
    """Retrieves article information from article_change"""

    with conn.cursor() as cur:

        cur.execute("""SELECT article_id, article_url, change_type,\
            previous_version, current_version, last_scraped, current_scraped,
                    similarity FROM changes.article_change;""")

        data = cur.fetchall()

    return pd.DataFrame(data, columns=["article_id", "article_url",
                                       "change_type", "previous_version", "current_version",
                                       "last_scraped", "current_scraped", "similarity"])


@st.cache_data
def retrieve_author(article_id: int) -> list:
    """Retrieves authors for selected article_id. Returns a list"""

    with conn.cursor() as cur:
        cur.execute("""SELECT au.author_name
                    FROM author au JOIN article_author aa ON au.author_id
                    = aa.author_id JOIN article ar ON ar.article_id =
                    aa.article_id WHERE aa.article_id = %s;""", [article_id])
        authors = cur.fetchall()
        return [author[0] for author in authors]


def format_article_change(block: str) -> list:
    """Formats article_change entry block into a list"""

    return block.split("£$")[1:]


def format_change_column(change: str) -> str:
    """Formats change column to title"""
    return change.title()


def highlighted_text(changes: list, symbol: str, colour: str) -> None:
    """Displays highlighted changes side by side"""

    string_builder = []
    for word in changes.split("§%")[1:]:
        if len(word) > 0:
            if word[0] == symbol:
                word = word.replace(symbol, " ")
                string_builder.append((word, "", colour))
            else:
                string_builder.append((" " + word))
    annotated_text(string_builder)


def dash_header():
    """Creates a dashboard header"""
    st.image("header_image.png")


def changes_per_source_bar_chart(articles_joined_df: pd.DataFrame) -> None:
    """Displays a bar chart of number of changes per source"""
    data = articles_joined_df.copy().groupby(
        "source").size().reset_index(name="count")
    fig = px.bar(
        data,
        x="source",
        y="count",
        labels={"source": "News Source", "count": "Count"},
        color="source",
        title="Number of Article Changes per Source",

    )
    st.plotly_chart(fig, theme="streamlit", use_container_width=False)


def total_articles_scraped(articles_df: pd.DataFrame):
    """Displays a metric of number of scraped articles"""
    total_articles_scraped = articles_df.shape[0]
    st.metric("Total articles scraped:", total_articles_scraped)


def display_article_changes_above_number(article_changes: pd.DataFrame, threshold: int):
    """Displays how many articles have changes over the threshold"""
    article_changes = article_changes.copy()
    changes = article_changes["article_id"].value_counts(
    ).reset_index()
    changes = changes[changes["count"] > threshold]
    st.metric(f"More than {threshold} changes to article:", changes.shape[0])


def display_one_article(article_changes: pd.DataFrame) -> None:
    """Displays a page for a selected article"""
    article_changes = article_changes.copy()
    st.write("Original headline:")
    article_url = article_changes["article_url"].iloc[0]
    heading = article_changes["heading"].iloc[0]
    st.markdown(f"# {heading}")
    image = get_image(article_url)
    if image:
        st.image(image)

    st.write(f"URL: {article_url}")
    st.markdown(f"## Total changes: {article_changes.shape[0]}")

    tuples = article_changes.to_records(index=False)
    for one_tuple in tuples:
        display_article_change(one_tuple)


def display_article_change(article_change: tuple) -> None:
    """An add-on that displays a single change"""

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.write(f"### Type of change: {article_change[2]}")
        st.write("**Previous version:**")
        for change in article_change[3]:
            highlighted_text(change, "-", "#84c9ff")
    with col2:
        st.markdown(f"### Similarity: {article_change[7]}%")
        st.write("**Current version:**")
        for change in article_change[4]:
            highlighted_text(change, "+", "#fe2b2b")


def mission_statement() -> None:
    """Displays the mission statement"""
    st.markdown("### Who are we?")
    st.markdown("""**News sources often change their articles without public disclosure.
                In the spirit of transparency and accountability, we want to change this.**""")
    st.markdown("""**The News Change Tracker allows you to track changes from publications, in real time.**""")


def heading_vs_body_changes_pie_chart(articles_joined_df: pd.DataFrame) -> None:
    """Displays the number of heading changes and number """
    articles_joined_df = articles_joined_df.copy()
    data = articles_joined_df.groupby(
        "change_type").size().reset_index(name="count")
    data.columns = ["Change Type", "count"]
    plot = alt.Chart(data, title="Article Change Types").mark_bar().encode(
    x='Change Type',
    y='count'
)

    st.altair_chart(plot, use_container_width=True, theme="streamlit")


def display_authors(article_changes: pd.DataFrame) -> None:
    """Displays the authors"""
    article_changes = article_changes.copy()
    article_changes = article_changes.explode(column=["author"])
    data = article_changes.groupby(
        "author").size().reset_index(name="count")
    st.write("---")
    st.write(f"## Authors on record: {data.shape[0]}")


def display_authors_and_changes(article_changes: pd.DataFrame) -> None:
    """Displays the authors and their changes """
    article_changes = article_changes.copy()
    article_changes = article_changes.explode(column=["author"])
    data = article_changes.groupby(
        "author").size().reset_index(name="count").sort_values(by="count", ascending=False)[:10]
    data.columns = ["Author", "Count"]
    plot = alt.Chart(data, title="Number of Changes per Author").mark_bar().encode(
    x='Author',
    y='Count'
)
    st.altair_chart(plot, use_container_width=True, theme="streamlit")


def display_change_counts(article_changes: pd.DataFrame) -> None:
    """Displays the authors and their changes """
    article_changes = article_changes.copy()
    article_changes = article_changes.explode(column=["author"])
    data = article_changes.groupby(
        "author").size().reset_index()
    data = data[0].value_counts().reset_index()
    data.columns = ["Count", "Authors"]
    plot = alt.Chart(data, title="Authors per Number of Article Changes").mark_bar().encode(
    x="Count",
    y="Authors"
)
    st.altair_chart(plot, theme="streamlit")


def changed_vs_unchaged_pie_chart(articles_joined_df: pd.DataFrame, articles: pd.DataFrame) -> None:
    """Displays the number of heading changes and number """
    articles_joined_df = articles_joined_df.copy()
    articles = articles.copy()
    changed_count = articles_joined_df.groupby("article_id").size().reset_index(name="count").shape[0]
    article_count = articles.shape[0] - changed_count
    ratio = pd.DataFrame({"Change Status": ["Changed", "Unchanged"], "Count" : [changed_count, article_count]})
    plot = alt.Chart(ratio, title="Proportion of Recorded Articles Changed").encode(
    x='Change Status',
    y='Count'
)

    st.altair_chart(plot.mark_bar() + plot.mark_text(align='left', dx=2), use_container_width=True)


def display_article_with_most_changes(articles_changes_df: pd.DataFrame) -> None:
    """Displays the article information with the most changes"""
    articles_changes_df = articles_changes_df.copy()

    most_changes_id = int(articles_changes_df["article_id"].value_counts(
    ).reset_index().iloc[0]["article_id"])

    most_changed_article = articles_changes_df[articles_changes_df["article_id"]
                                               == most_changes_id]

    st.markdown("### Article with most changes:")
    st.markdown(f"**Article ID = {most_changed_article['article_id'].iloc[0]}, \
                {most_changed_article.count().iloc[0]} changes.**")
    st.write("### Example change:")
    data = most_changed_article.to_records(index=False)[0]
    display_article_change(data)


def display() -> None:
    """Displays the dashboard"""

    try:

        warnings.filterwarnings("ignore")
        st.set_page_config(
        page_title="News Change Tracker", layout="wide")

        # set-up the data
        article_changes = retrieve_article_changes()
        articles = retrieve_article_info()
        article_changes["author"] = article_changes["article_id"].apply(retrieve_author)
        article_changes.to_csv("changes_column.csv")
        article_changes["previous_version"] = article_changes["previous_version"]\
            .apply(format_article_change)
        article_changes["current_version"] = article_changes["current_version"]\
            .apply(format_article_change)
        article_changes["change_type"] = article_changes["change_type"].\
            apply(format_change_column)
        article_changes["heading"] = article_changes["article_id"].apply(retrieve_heading)

        articles_joined = pd.merge(
            article_changes, articles, how="left", on="article_id")
        sources = articles_joined["source"].unique()

        # multiselect
        selection_df = sorted(article_changes["article_id"].drop_duplicates())
        selection_df.insert(0, "Homepage")
        selected_articles = st.sidebar.selectbox("Article ID", options=selection_df, index=0)
        selected_sources = st.sidebar.selectbox(
            "Source", options=sorted(sources))

        # homepage
        if isinstance(selected_articles, str):
            dash_header()
            st.markdown("---")
            mission_statement()
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                total_articles_scraped(articles)
            with col2:
                display_article_changes_above_number(article_changes, 5)
            with col3:
                display_article_changes_above_number(article_changes, 10)
            st.markdown("---")
            st.write("## Changes Overview")
            changes_per_source_bar_chart(articles_joined)
            col1, col2 = st.columns(2)
            with col1:
                changed_vs_unchaged_pie_chart(article_changes, articles)
            with col2:
                heading_vs_body_changes_pie_chart(articles_joined)
            display_authors(article_changes)
            col1, col2= st.columns(2)
            with col1:
                display_change_counts(article_changes)
            with col2:
                display_authors_and_changes(article_changes)

            st.write("---")
            display_article_with_most_changes(article_changes)


        # one selection
        if isinstance(selected_articles, int):
            working_article = article_changes[article_changes["article_id"]
                                              == selected_articles]
            display_one_article(working_article)
            working_article.loc[:, "image"] = working_article.loc[:, "article_url"].apply(
                lambda x: get_image(x))

        # return article_changes, articles -
    except KeyboardInterrupt:
        print("User stopped the program.")
    finally:
        conn.close()


if __name__ == "__main__":

    display()
