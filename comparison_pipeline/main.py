"""Main file to be called once"""

from extract import extract_data
from transform import transform_data

if __name__ == "__main__":

    extract_data()

    transform_data()
