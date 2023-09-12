"""Dashboard script"""

from os import environ
from dotenv import load_dotenv
import pandas as pd
from psycopg2 import connect
from psycopg2.extensions import connection
import streamlit as st
import plotly.express as px
from annotated_text import annotated_text


def get_db_connection() -> connection:
    """Returns connection to the rds database"""

    load_dotenv()

    return connect(host=environ["DB_HOST"],
                       user=environ["DB_USER"],
                       password=environ["DB_PASSWORD"],
                       port=environ["DB_PORT"],
                       dbname=environ["DB_NAME"])


def retrieve_article_info(conn: connection) -> pd.DataFrame:
    """Retrieves all article information. Returns dataframe"""

    with conn.cursor() as cur:

        cur.execute("""SELECT ar.article_id, ar.article_url,
                    ar.source, ar.created_at
                FROM article ar;""")

        data = cur.fetchall()

    return pd.DataFrame(data, columns=["article_id", "article_url",\
                                "source", "created_at"])


def retrieve_article_changes(conn: connection) -> pd.DataFrame:
    """Retrieves article information from article_change"""

    with conn.cursor() as cur:

        cur.execute("""SELECT article_id, article_url, change_type,\
            previous_version, current_version, last_scraped, current_scraped,
                    similarity FROM changes.article_change;""")

        data = cur.fetchall()

    return pd.DataFrame(data, columns=["article_id", "article_url", \
            "change_type", "previous_version", "current_version", \
            "last_scraped", "current_scraped", "similarity"])


def retrieve_author(conn: connection, article_id: int) -> list:
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

    block = block.split("£$")
    formatted_block = []

    for segment in block:
        segment = segment.replace("§%", "")
        formatted_block.append(segment)
    return formatted_block[1:]


def highlighted_text() -> None:
    """Displays highlighted changes side by side"""

    changes = """ I
+don't
+know
+if
+I
+like
+or
+not
like
tomatoes
and
fruits
-jcgjcgcjgjcg"""
    string_builder = []
    changes = changes.split('\n')
    print(changes)
    for word in changes:
        if word[0] == '+':
            word = word.replace("+", " ")
            string_builder.append((word, "", "#81d654"))
        elif word[0] == '-':
            word = word.replace("-", " ")
            string_builder.append((word, "", "#f07ff0"))
        else:
            string_builder.append((" " + word))
    annotated_text(string_builder)


def dash_header():
    """Creates a dashboard header"""
    st.image("header_image.png")
    st.title("News Change Tracker")


def changes_per_source_bar_chart(articles_joined_df):
    """Displays a bar chart of number of changes per source"""
    data = articles_joined_df.groupby("source").size().reset_index(name="count")
    fig = px.bar(
        data,
        x="source",
        y="count",
        labels={"source": "News Source", "0": "Number of Changes"},
        color = "source",
        title = "Article Changes per Source",
        
    )
    st.plotly_chart(fig, theme="streamlit", use_container_width=False)
    


def total_articles_scraped(articles_df:pd.DataFrame):
    """Displays a metric of number of scraped articles"""
    total_articles_scraped = articles_df.shape[0]
    st.metric("Total articles scraped:", total_articles_scraped)


def mission_statement() -> None:
    """Displays the mission statement"""
    st.markdown("### Why is this project necessary?")
    st.markdown("Your text here")


def display() -> None:
    """Displays the dashboard"""

    try:
        db_conn = get_db_connection()

        # set-up the data
        article_changes = retrieve_article_changes(db_conn)
        articles = retrieve_article_info(db_conn)
        articles["authors"] = articles["article_id"].apply(lambda x:\
                                retrieve_author(db_conn, x))
        article_changes["previous_version"] = article_changes["previous_version"]\
        .apply(format_article_change)
        article_changes["current_version"] = article_changes["current_version"]\
        .apply(format_article_change)
        article_changes.to_csv("changes_column.csv")

        articles_joined = pd.merge(article_changes, articles, how="left", on="article_id")
        # homepage
        dash_header()
        mission_statement()
        total_articles_scraped(articles)
        sources = articles_joined["source"].unique()
        
        selected_articles = st.sidebar.multiselect("Article ID", options=sorted(articles_joined["article_id"]))
        selected_sources = st.sidebar.multiselect("Source", options=sorted(sources))


        if len(selected_articles) != 0:
            articles_joined = articles_joined[articles_joined["article_id"].isin(selected_articles)]
            articles_joined = articles_joined[articles_joined["source"].isin(selected_sources)]

        changes_per_source_bar_chart(articles_joined)


        # return article_changes, articles -
    except KeyboardInterrupt:
        print("User stopped the program.")
    finally:
        db_conn.close()



if __name__ == "__main__":
    display()
