import pytest

import banana_dispenser.data_process as dp
import pandas as pd
from expression import Some


def test_get_orders_tabls():
    people_df_op = Some("tests/data/people_list.sample.csv").pipe(
        dp.open_list_file, dp.people_df_validator
    )
    objects_df_op = Some("tests/data/objects.sample.csv").pipe(
        dp.open_list_file, dp.objects_df_validator
    )
    # print(objects_df_op.value)
    orders_df_op = dp.combine_to_orders_table(people_df_op, objects_df_op)
    print(orders_df_op.value)
    print(orders_df_op.value.info())


# def test()
