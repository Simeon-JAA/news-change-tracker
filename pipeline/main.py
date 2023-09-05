"""Main file where whole etl will run in docker"""

from extract import extract_data
from transform import transform_data

if __name__ == "__main__":

    extract_data()

    transform_data()