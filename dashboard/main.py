"""Dashboard script"""

from os import environ
from dotenv import load_dotenv
import pandas as pd
from psycopg2 import connect
from psycopg2.extensions import connection
import streamlit as st
from annotated_text import annotated_text


def get_db_connection() -> connection:
    """Returns connection to the rds database"""

    load_dotenv()

    return connect(host=environ["DB_HOST"],
                       user=environ["DB_USER"],
                       password=environ["DB_PASSWORD"],
                       port=environ["DB_PORT"],
                       dbname=environ["DB_NAME"])


def retrieve_article_info() -> pd.DataFrame:
    """Retrieves all article information. Returns dataframe"""

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


def display() -> None:
    """Displays the dashboard"""

    highlighted_text()


if __name__ == "__main__":
    display()
