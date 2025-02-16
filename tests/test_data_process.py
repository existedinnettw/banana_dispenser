import os
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from expression import Some, Ok
from pytest_mock import MockFixture

import banana_dispenser.data_process as dp


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({"id": [1, 2], "value": ["a", "b"]}).set_index("id")


def test_csv_with_id_column(mocker: MockFixture, sample_dataframe):
    test_csv = "test.csv"
    mock_read_csv = mocker.patch("pandas.read_csv", return_value=sample_dataframe)

    result = dp.open_list_file(Some(test_csv))

    assert result.is_ok()
    pd.testing.assert_frame_equal(result.ok, sample_dataframe)
    mock_read_csv.assert_called_once_with(test_csv, skipinitialspace=True)


def test_empty_csv_file(mocker: MockFixture):
    test_csv = "empty.csv"
    mocker.patch("pandas.read_csv", side_effect=pd.errors.EmptyDataError)

    result = dp.open_list_file(Some(test_csv))

    assert result.is_error()
    assert "Error reading CSV" in result.error


def test_valid_people_df():
    input_df = pd.DataFrame({"name": ["John", "Jane"]})
    input_df_res = Ok(input_df)

    result = dp.people_df_validator(input_df_res)

    assert result.is_ok()
    assert "name" in result.ok.columns
    assert result.ok["name"].dtype == "object"


def test_valid_object_df():
    input_df = pd.DataFrame(
        {
            "id": [6, 8, 11],
            "object": ["banana", "apple", "orange"],
            "people_id": [1, 22, 23],
            "pickup_datetime": [pd.NaT, pd.NaT, pd.NaT],
        }
    ).set_index("id")
    input_df_res = Ok(input_df)

    result = dp.objects_df_validator(input_df_res)

    assert result.is_ok()
    assert all(
        col in result.ok.columns for col in ["object", "people_id", "pickup_datetime"]
    )
    assert result.ok["pickup_datetime"].dtype == "datetime64[ns, UTC]"
    assert result.ok["object"].dtype == object
    assert result.ok["object"].dtype == pd.Int64Dtype


def test_get_orders_table():
    people_df_op = Some("tests/data/people_list.sample.csv").pipe(
        dp.open_list_file, dp.people_df_validator
    )
    objects_df_op = Some("tests/data/objects.sample.csv").pipe(
        dp.open_list_file, dp.objects_df_validator
    )

    orders_df_op = dp.combine_to_orders_table(people_df_op, objects_df_op)

    assert orders_df_op.is_ok()
    assert orders_df_op.ok.index.name == "id"


def test_export_df_list_file_csv(tmp_path, sample_dataframe):
    file_path = tmp_path / "test.csv"
    file_path_op = Some(file_path)

    result = dp.export_df_list_file(Some(sample_dataframe), file_path_op)

    assert result.is_ok()
    saved_df = pd.read_csv(file_path).set_index("id")
    pd.testing.assert_frame_equal(sample_dataframe, saved_df)


def test_export_df_list_file_excel(tmp_path, sample_dataframe):
    file_path = tmp_path / "test.xlsx"
    file_path_op = Some(file_path)

    result = dp.export_df_list_file(Some(sample_dataframe), file_path_op)

    assert result.is_ok()
    saved_df = pd.read_excel(file_path).set_index("id")
    pd.testing.assert_frame_equal(sample_dataframe, saved_df)


def test_export_df_list_file_unsupported_format(tmp_path, sample_dataframe):
    file_path = tmp_path / "test.txt"
    file_path_op = Some(file_path)

    result = dp.export_df_list_file(Some(sample_dataframe), file_path_op)

    assert result.is_error()
    assert "Unsupported file format" in result.error


def test_insert_conflict_to_path():
    assert dp.insert_conflict_to_path("abc/xxx.csv") == "abc/xxx.conflict.csv"
    assert dp.insert_conflict_to_path("abc/xxx") == "abc/xxx.conflict"
    assert dp.insert_conflict_to_path("abc/xxx.tar.gz") == "abc/xxx.tar.conflict.gz"


def test_export_and_save_back_origin_path(tmp_path, sample_dataframe):
    file_path = tmp_path / "test.csv"
    ori_touch_time = datetime.now() - timedelta(days=1)

    sample_dataframe.to_csv(file_path)
    os.utime(file_path, (ori_touch_time.timestamp(), ori_touch_time.timestamp()))

    dp.export_and_save_back_origin_path(
        sample_dataframe, str(file_path), ori_touch_time
    )

    saved_df = pd.read_csv(file_path).set_index("id")
    pd.testing.assert_frame_equal(sample_dataframe, saved_df)

    df_modified = pd.DataFrame({"id": [3, 4], "value": ["c", "d"]})
    df_modified.to_csv(file_path)

    dp.export_and_save_back_origin_path(
        sample_dataframe, str(file_path), ori_touch_time
    )

    conflict_file_path = dp.insert_conflict_to_path(str(file_path))
    assert Path(conflict_file_path).exists()

    conflict_df = pd.read_csv(conflict_file_path).set_index("id")
    pd.testing.assert_frame_equal(sample_dataframe, conflict_df)
