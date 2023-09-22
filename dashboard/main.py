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



def get_db_connection() -> connection:
    """Returns connection to the rds database"""

    load_dotenv()

    return connect(host=environ["DB_HOST"],
                   user=environ["DB_USER"],
                   password=environ["DB_PASSWORD"],
                   port=environ["DB_PORT"],
                   dbname=environ["DB_NAME"])


conn = get_db_connection()


# setup data
def retrieve_highest_change_count() -> str:
    """Retrieves the higest article change count"""

    with conn.cursor() as cur:
        cur.execute("""SELECT COUNT(article_id), article_id FROM changes.article_change
                    GROUP BY article_id ORDER BY COUNT(article_id) DESC LIMIT 1;""")

        data = cur.fetchone()[0]

        return data


def retrieve_article_change_with_id(article_id: int) -> pd.DataFrame:
    """Retrieves article information from article_change by id"""

    with conn.cursor() as cur:

        cur.execute("""SELECT article_id, article_url, change_type,\
            previous_version, current_version, last_scraped, current_scraped,
                    similarity FROM changes.article_change WHERE article_id = %s;""", [str(article_id)])

        data = cur.fetchall()

    return pd.DataFrame(data, columns=["article_id", "article_url",
                                       "change_type", "previous_version", "current_version",
                                       "last_scraped", "current_scraped", "similarity"])


def retrieve_authors_by_id(article_id: int) -> list:
    """Retrieves all authors for the given article_id"""

    with conn.cursor() as cur:
        cur.execute("""SELECT author_name FROM author a LEFT JOIN article_author
                    aa ON a.author_id = aa.author_id WHERE aa.article_id = %s;"""\
                    , [str(article_id)])
        data = cur.fetchall()
        if len(data) > 0:
            return ", ".join([author[0] for author in data])
        else:
            return "None recorded"


def retrieve_article_with_most_changes() -> pd.DataFrame:
    """Retrieves article with most changes"""

    with conn.cursor() as cur:
        cur.execute("""SELECT article_id, article_url, count(article_id)
                    FROM changes.article_change
                    GROUP BY article_id,article_url ORDER BY
                    COUNT(article_id) DESC LIMIT 10;""")

        data = cur.fetchall()

    return pd.DataFrame(data, columns=["Heading", "URL",
                                       "Number of Changes"])


def retrieve_article_count() -> str:
    """Retrieves a current article count"""

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM article;")
        data = cur.fetchone()[0]
        return data


def retrieve_author_count() -> str:
    """Retrieves a current author count"""

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM author;")
        data = cur.fetchone()[0]
        return data


def retrieve_article_count_above_number(above: str) -> str:
    """Retrieves article count with changes above number"""\

    with conn.cursor() as cur:
        cur.execute("""SELECT COUNT(*) FROM (SELECT article_id
    FROM changes.article_change GROUP BY article_id HAVING COUNT(article_id)
     > %s) AS subquery;""", [above])
        data = cur.fetchone()[0]
        return data


def retrieve_articles_per_source() -> pd.DataFrame:
    """Returns the amount of articles per source"""
    with conn.cursor() as cur:
        cur.execute("""SELECT count(article_id), source from article GROUP BY source;""")
        data = cur.fetchall()
        return pd.DataFrame(data, columns=["Count", "Source"])


def retrieve_author_change_count() -> pd.DataFrame:
    """Retrieves amount of changes per author"""
    with conn.cursor() as cur:
        cur.execute("""SELECT ar.author_name, COUNT(c.article_id) as change_count
                FROM article_author a
                RIGHT JOIN author ar ON ar.author_id = a.author_id
                RIGHT JOIN changes.article_change c ON a.article_id = c.article_id
                GROUP BY ar.author_name
                ORDER BY change_count DESC LIMIT 12;""")
        data = cur.fetchall()[1:]
        return pd.DataFrame(data, columns=["Author Name", "Changes"])


def retrieve_author_count_per_change() -> pd.DataFrame:
    """Retrieves number of authors per number of changes"""

    with conn.cursor() as cur:
        cur.execute("""SELECT ar.author_name, COUNT(c.article_id) as change_count
                FROM article_author a
                LEFT JOIN author ar ON ar.author_id = a.author_id
                LEFT JOIN changes.article_change c ON a.article_id = c.article_id
                GROUP BY ar.author_name
                ORDER BY ar.author_name ASC;""")
        data = cur.fetchall()
        return pd.DataFrame(data, columns=["Author Count", "Changes"])


def retrieve_changed_vs_unchaged_counts() -> pd.DataFrame:
    """Retrieves counts for articles in changes.article_change and articles
    not on the table"""

    with conn.cursor() as cur:
        cur.execute("""SELECT COUNT(DISTINCT(article_id)) from
                    changes.article_change;""")
        changed = cur.fetchone()[0]
        unchanged = retrieve_article_count() - changed
        return pd.DataFrame({"Status": ["Changed", "Unchanged"], "Count": [changed, unchanged]})


def retrieve_change_type_counts() -> pd.DataFrame:
    """Retrieves counts for change_types"""

    with conn.cursor() as cur:
        cur.execute("""SELECT change_type, COUNT(*)
        FROM changes.article_change
        GROUP BY change_type;""")
        data = cur.fetchall()
        return pd.DataFrame(data, columns=["Change Type", "Count"])


def retrieve_heading(article_id: str) -> str:
    """Retrieves an original heading for a single article"""

    with conn.cursor() as cur:
        cur.execute("""SELECT heading FROM article_version WHERE article_id =
                    %s ORDER BY scraped_at ASC LIMIT 1;""", [article_id])
        data = cur.fetchone()[0]
        return data


# searchbar
def retrieve_article_id_with_headlines() -> pd.DataFrame:
    """Retrieves article_ids from articles that had changes with original headlines"""

    with conn.cursor() as cur:
        cur.execute("""SELECT DISTINCT(c.article_id) as id, v.heading, c.similarity
                     from (SELECT a.article_id, a.similarity
                FROM changes.article_change a
                JOIN ( SELECT article_id, MIN(similarity) as min_similarity
                FROM changes.article_change GROUP BY article_id
                ) b ON a.article_id = b.article_id AND a.similarity = b.min_similarity) c
                LEFT JOIN (SELECT article_id, heading FROM article_version
                WHERE (article_id, scraped_at) IN (SELECT article_id, MIN(scraped_at)
                FROM article_version GROUP BY article_id)) v ON c.article_id =
                v.article_id ORDER BY id ASC;""")
        data = cur.fetchall()
        return pd.DataFrame(data, columns=["article_id", "heading", "similarity"])


def retrieve_change_count() -> pd.DataFrame:
    """Retrieves a count in changes.article_change by article_id"""

    with conn.cursor() as cur:
        cur.execute("""SELECT article_id, COUNT(article_id) FROM changes.article_change
                    GROUP BY article_id;""")
        data = cur.fetchall()
        return pd.DataFrame(data, columns=["article_id", "change_count"])


# homepage details
def dash_header():
    """Creates a dashboard header"""
    st.image("header_image.png")


def mission_statement() -> None:
    """Displays the mission statement"""
    st.markdown("### Who are we?")
    st.markdown("""**News sources often change their articles without public disclosure.
                In the spirit of transparency and accountability, we want to change this.**""")
    st.markdown("""**The News Change Tracker allows you to track changes from publications, in real time.**""")
    st.markdown("""Please select stories by title and source on the left sidebar.
                You may also filter by similarity percentage or number of changes to article.""")


def total_numbers():
    """Displays a metric of number of scraped articles"""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total articles scraped:", retrieve_article_count())
    with col2:
        st.metric(f"More than 5 changes to article:", retrieve_article_count_above_number("5"))
    with col3:
        st.metric(f"More than 10 changes to article:", retrieve_article_count_above_number("10"))
    with col4:
        sources = retrieve_articles_per_source()["Source"].count()
        st.metric(f"Total news sources:", sources)


def searchbar_setup() -> pd.DataFrame:
    """Sets up the searchbar data"""
    id_and_headings = retrieve_article_id_with_headlines()
    id_and_headings = id_and_headings.merge(retrieve_change_count(), how="left",\
                        on="article_id")
    id_and_headings["change_count"] = id_and_headings["change_count"].map(int)
    id_and_headings["similarity"] = id_and_headings["similarity"].map(int)
    id_and_headings.loc[-1] = [0, "--Homepage--", 0, 2]
    id_and_headings.index = id_and_headings.index + 1
    id_and_headings = id_and_headings.sort_index()
    return id_and_headings


# one article page
def get_image(url: str) -> None:
    """Gets article image"""
    article = requests.get(url, timeout=10)
    soup = bs(article.content, 'lxml')
    picture = soup.find('img', {"srcset": re.compile(".*")})["src"]
    return picture


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


def display_one_article(article_changes: pd.DataFrame, heading: str) -> None:
    """Displays a page for a selected article"""
    article_changes = article_changes.copy()
    article_changes["previous_version"] = article_changes["previous_version"].apply(format_article_change)
    article_changes["current_version"] = article_changes["current_version"].apply(format_article_change)
    article_url = article_changes["article_url"].iloc[0]
    st.markdown(f"# [{heading}](%s)"% article_url)
    image = get_image(article_url)
    if image:
        st.image(image, width=700)
    st.markdown(f"Authors: {retrieve_authors_by_id(article_changes['article_id'].iloc[0])}")
    st.markdown(f"## Total changes: {article_changes.shape[0]}")

    tuples = article_changes.to_records(index=False)
    for one_tuple in tuples:
        display_article_change(one_tuple)


def display_article_change(article_change: tuple) -> None:
    """An add-on that displays a single change"""

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.write(f"### Type of change: {article_change[2].title()}")
        st.write(f"**Previous version recorded at: {article_change[5].strftime('%Y-%m-%d %H:%M:%S')}**")
        for change in article_change[3]:
            highlighted_text(change, "-", "#ff774d")
    with col2:
        st.markdown(f"### Similarity: {article_change[7]}%")
        st.write(f"**Current version recorded at: {article_change[6].strftime('%Y-%m-%d %H:%M:%S')}**")
        for change in article_change[4]:
            highlighted_text(change, "+", "#8cbe48")


# charts
def changes_per_source_bar_chart() -> None:
    """Displays a bar chart of number of changes per source"""
    data = retrieve_articles_per_source()
    fig = px.bar(
        data,
        x="Source",
        y="Count",
        labels={"Source": "News Source", "Count": "Count"},
        color="Source",
        title="Article Change Count per Source",

    )
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)


def heading_vs_body_changes_chart() -> None:
    """Displays the count of change types"""
    data = retrieve_change_type_counts()
    data["Change Type"] = data["Change Type"].apply(lambda x: x.title())
    plot = alt.Chart(data, title="Article Change Types").mark_bar().encode(
    x='Count',
    y='Change Type'
)
    st.altair_chart(plot, use_container_width=True, theme="streamlit")


def display_authors() -> None:
    """Displays the authors"""
    st.write("---")
    st.write(f"## Authors on record: {retrieve_author_count()}")


def display_authors_and_changes() -> None:
    """Displays the authors and their changes """
    data = retrieve_author_change_count()
    plot = alt.Chart(data, title="Number of Changes per Author (Top 12)").mark_bar().encode(
    x='Changes',
    y='Author Name'
)
    st.altair_chart(plot, use_container_width=True, theme="streamlit")


def display_change_counts_for_authors() -> None:
    """Displays the authors and their changes """
    data = retrieve_author_count_per_change()
    data = data.groupby(["Changes"]).count().reset_index()

    plot = alt.Chart(data, title="Authors per Number of Article Changes").mark_bar().encode(
    x="Changes:O",
    y="Author Count"
)
    st.altair_chart(plot, theme="streamlit")


def changed_vs_unchaged_barchart() -> None:
    """Displays a chart for changed vs unchaged article counts"""

    data = retrieve_changed_vs_unchaged_counts()
    plot = alt.Chart(data, title="Change Status of Recorded Articles").mark_bar()\
    .encode(
    x='Count',
    y='Status'
)

    st.altair_chart(plot, use_container_width=True)


def display_article_with_most_changes() -> None:
    """Displays the article information with the most changes"""
    article = retrieve_article_with_most_changes()
    article["Heading"] = article["Heading"].apply(retrieve_heading)

    st.markdown("### Articles with the most changes:")
    st.table(article)


def display() -> None:
    """Displays the dashboard"""

    try:
        warnings.filterwarnings("ignore")
        st.set_page_config(
        page_title="News Change Tracker", layout="wide")

        # searchbar
        sources = retrieve_articles_per_source()["Source"]
        id_and_headings = searchbar_setup()
        max_changes = int(retrieve_highest_change_count())
        changes = [str(number) for number in range(1, max_changes + 1)]
        with st.sidebar:
            start_pct, end_pct = st.select_slider("Select a similarity percentage", \
        options=["0", "10", "20", "30", "40", "50", "60", "70", "80", "90", "100"], value=("0", "100"))
        with st.sidebar:
            start_chg, end_chg = st.select_slider("Select number of changes to article",\
        options=changes, value=("1", str(max_changes)))

            selected_articles = st.selectbox("Original Article Title", \
                options=id_and_headings[(id_and_headings["similarity"] >= int(start_pct)) &\
                                    (id_and_headings["similarity"] <= int(end_pct)) &\
                                (id_and_headings["change_count"] >= int(start_chg)) & \
                                    (id_and_headings["change_count"] <= int(end_chg))]["heading"], index=0)

            selected_sources = st.selectbox("Source", options=sorted(sources))

        # homepage
        if selected_articles == "--Homepage--":
            dash_header()
            st.markdown("---")
            mission_statement()
            st.markdown("---")
            total_numbers()
            st.markdown("---")
            st.write("## Changes Overview")
            col1, col2 = st.columns(2)
            with col1:
                changes_per_source_bar_chart()
            with col2:
                heading_vs_body_changes_chart()
                changed_vs_unchaged_barchart()
            display_authors()
            col1, col2= st.columns(2)
            with col1:
                display_change_counts_for_authors()
            with col2:
                display_authors_and_changes()

            st.write("---")
            display_article_with_most_changes()
        else:
        # one selection
            article_id = id_and_headings[id_and_headings["heading"] == selected_articles]\
                .iloc[0]["article_id"]
            working_article = retrieve_article_change_with_id(article_id)
            display_one_article(working_article, selected_articles)
            working_article.loc[:, "image"] = working_article.loc[:, "article_url"].apply(
                lambda x: get_image(x))

    except KeyboardInterrupt:
        print("User stopped the program.")
    finally:
        conn.close()


if __name__ == "__main__":

    display()
