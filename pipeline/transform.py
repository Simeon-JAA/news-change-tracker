"""Transforms the data by flattening and cleaning before it goes into the load stage"""

import pandas as pd
from pandas import DataFrame

def get_rss_feed_df(file_path: str) -> DataFrame:
    """Returns the scraped article csv as a DataFrame"""
    df = pd.read_csv(file_path)
    return df


def get_scraped_articles_df(file_path: str) -> DataFrame:
    """Returns the rss_feed csv as a DataFrame"""
    df = pd.read_csv(file_path)
    return df


def format_time_to_timestamp(time_in_col: str) -> str:
    """Formats time to timestamp format to load into postgres"""
    
    month_to_number =  {"jan": "01", "feb": "02", "mar": "03",
                        "apr": "04", "may": "05", "jun": "06",
                        "jul": "07", "aug": "08", "sep": "09",
                        "oct": "10", "nov": "11", "dec": "12",
                        }
    time_in_col = time_in_col.split(" ")
    time_in_col = time_in_col[1:]

    time_in_col.insert(0 , time_in_col.pop(2))
    time_in_col.insert(1 , time_in_col.pop(2))

    time_in_col[1] = month_to_number[time_in_col[1].lower()]


    if time_in_col[-1].upper()  == "GMT":
         date = "-".join(time_in_col[:-2])
         time = time_in_col[-2]
         return f"{date} {time}"
    return 


def format_rss_feed_df(df: DataFrame) -> DataFrame:
    """Formats rss feed dataframe columns before saving to csv df"""

    df["published"] = df["published"].apply(format_time_to_timestamp)
    df["id"] = df["id"].apply(lambda row: row.strip())
    df = df[["id", "title", "published"]]

    return df


def format_scraped_articles_df(df: DataFrame) -> DataFrame:
    """Formats scraped_articles dataframe columns before saving to csv df"""

    return df

    
if __name__ == "__main__":
    
    rss_feed_df = get_rss_feed_df("rss_feed.csv")

    rss_feed_df = format_rss_feed_df(rss_feed_df)

    scraped_article_df = get_scraped_articles_df("scraped_articles.csv")

    print(scraped_article_df.columns)

    # joined_data = pd.merge(left=scraped_article_df,
    #                         right=rss_feed_df,
    #                         left_on="url",
    #                         right_on="id")

    # print(joined_data.columns)

