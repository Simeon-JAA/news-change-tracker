"""Main file to be called once"""

from extract import extract_data
from compare import compare_data
from load import load_data


if __name__ == "__main__":

    extract_data()

    compare_data()

    load_data()
