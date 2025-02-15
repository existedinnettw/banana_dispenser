import pytest

import banana_dispenser.data_process as dp
import pandas as pd
from expression import Some, Ok
from pytest_mock import MockFixture
from datetime import datetime, timedelta
from pathlib import Path
import os
import numpy as np


# Successfully read and process CSV file with 'id' column
def test_csv_with_id_column(mocker: MockFixture):
    # Arrange
    test_csv = "test.csv"
    mock_df = pd.DataFrame({"id": [1, 2], "value": ["a", "b"]})
    mock_read_csv = mocker.patch("pandas.read_csv", return_value=mock_df)

    # Act
    result = dp.open_list_file(Some(test_csv))

    # Assert
    # print(result.ok)
    assert result.is_ok()
    pd.testing.assert_frame_equal(result.ok, mock_df.set_index("id"))
    mock_read_csv.assert_called_once_with(test_csv, skipinitialspace=True)


# Handle empty CSV/Excel files
def test_empty_csv_file(mocker: MockFixture):
    # Arrange
    test_csv = "empty.csv"
    mocker.patch("pandas.read_csv", side_effect=pd.errors.EmptyDataError)

    # Act
    result = dp.open_list_file(Some(test_csv))

    # Assert
    assert result.tag == "error"
    assert "Error reading CSV" in result.error


def test_valid_people_df():
    # Arrange
    input_df = pd.DataFrame({"name": ["John", "Jane"]})
    input_df_res = Ok(input_df)

    # Act
    result = dp.people_df_validator(input_df_res)

    # Assert
    assert result.is_ok()
    assert isinstance(result.ok, pd.DataFrame)
    assert "name" in result.ok.columns
    assert result.ok["name"].dtype == "object"


def test_valid_object_df():
    # Arrange
    input_df = pd.DataFrame(
        {
            "id": [6, 8, 11],
            "object": ["banana", "apple", "orange"],
            "people_id": [1, 22, 23],
            "pickup_datetime": [pd.NaT, pd.NaT, pd.NaT],
        }
    ).set_index("id")
    input_df_res = Ok(input_df)

    # Act
    result = dp.objects_df_validator(input_df_res)

    # Assert
    assert result.is_ok()
    assert isinstance(result.ok, pd.DataFrame)
    assert result.ok["pickup_datetime"].dtype == "datetime64[ns, UTC]"


def test_get_orders_table():
    people_df_op = Some("tests/data/people_list.sample.csv").pipe(
        dp.open_list_file, dp.people_df_validator
    )
    objects_df_op = Some("tests/data/objects.sample.csv").pipe(
        dp.open_list_file, dp.objects_df_validator
    )
    # print(objects_df_op.value)
    orders_df_op = dp.combine_to_orders_table(people_df_op, objects_df_op)
    assert orders_df_op.is_ok(), "\n{}\n".format(orders_df_op)
    assert orders_df_op.ok.index.name == "id"
    print(orders_df_op.ok)
    print(orders_df_op.ok.info())
    print(people_df_op.ok)
    print(objects_df_op.ok)


def test_insert_conflict_to_path():
    # Test with a simple file path
    assert dp.insert_conflict_to_path("abc/xxx.csv") == "abc/xxx.conflict.csv"

    # Test with a file path without an extension
    assert dp.insert_conflict_to_path("abc/xxx") == "abc/xxx.conflict"

    # Test with a file path with multiple dots
    assert dp.insert_conflict_to_path("abc/xxx.tar.gz") == "abc/xxx.tar.conflict.gz"


def test_export_and_save_back_origin_path(tmp_path):
    # Create a temporary DataFrame
    df = pd.DataFrame({"id": [1, 2], "value": ["a", "b"]}).set_index("id")

    # Create a temporary file path
    file_path = tmp_path / "test.csv"

    # Set the original touch time
    ori_touch_time = datetime.now() - timedelta(days=1)

    # Create the file and set its modification time
    df.to_csv(file_path)
    os.utime(file_path, (ori_touch_time.timestamp(), ori_touch_time.timestamp()))

    # Call the function
    dp.export_and_save_back_origin_path(df, str(file_path), ori_touch_time)

    # Check if the file was saved correctly
    saved_df = pd.read_csv(file_path).set_index("id")
    print(df, "\n", saved_df)
    pd.testing.assert_frame_equal(df, saved_df)

    # Modify the file to simulate a change
    df_modified = pd.DataFrame({"id": [3, 4], "value": ["c", "d"]})
    df_modified.to_csv(file_path)

    # Call the function again with the modified file
    dp.export_and_save_back_origin_path(df, str(file_path), ori_touch_time)

    # Check if the conflict file was created
    conflict_file_path = dp.insert_conflict_to_path(str(file_path))
    assert Path(conflict_file_path).exists()

    # Check if the conflict file contains the original data
    conflict_df = pd.read_csv(conflict_file_path).set_index("id")
    pd.testing.assert_frame_equal(df, conflict_df)
