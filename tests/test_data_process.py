import pytest

from banana_dispenser.data_process import check_id_as_index
import pandas as pd


def test_check_order():
    # people_df = pd.read_csv("tests/data/people_list.sample.csv", skipinitialspace=True)

    people_df = check_id_as_index(pd.read_excel("tests/data/people_list.sample.xlsx"))

    objects_df = check_id_as_index(
        pd.read_csv("tests/data/objects.sample.csv", skipinitialspace=True)
    )

    combined_df = objects_df.merge(
        people_df,
        how="inner",
        left_on="people_id",
        right_on="id",
        suffixes=(None, "_DROP"),
    ).filter(regex="^(?!.*DROP)")
    print(combined_df)
