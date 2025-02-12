import pytest

from banana_dispenser.data_process import open_list_file, combine_to_orders_table
import pandas as pd
from expression import Some


def test_get_orders_tabls():
    people_df_op = Some("tests/data/people_list.sample.csv").pipe(open_list_file)
    objects_df_op = Some("tests/data/objects.sample.csv").pipe(open_list_file)
    orders_df_op = combine_to_orders_table(people_df_op, objects_df_op)
    print(orders_df_op.value)


# def test()
