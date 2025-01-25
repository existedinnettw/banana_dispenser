import pytest

# from banana_dispenser.data_process import
import pandas as pd


def test_check_order():
    people_df = pd.read_csv("tests/data/people_list.sample.csv", skipinitialspace=True)
    print(people_df)
    objects_df = pd.read_csv("tests/data/objects.sample.csv", skipinitialspace=True)
    print(objects_df)
    combined_df = objects_df.merge(people_df, left_on="people_id", right_on="id")
    print(combined_df)
