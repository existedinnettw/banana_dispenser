import pytest

import banana_dispenser.data_process as dp
import pandas as pd
from expression import Some, Ok
from pytest_mock import MockFixture


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


def test_valid_df_with_name_column_returns_ok():
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


def test_get_orders_tabls():
    people_df_op = Some("tests/data/people_list.sample.csv").pipe(
        dp.open_list_file, dp.people_df_validator
    )
    objects_df_op = Some("tests/data/objects.sample.csv").pipe(
        dp.open_list_file, dp.objects_df_validator
    )
    # print(objects_df_op.value)
    orders_df_op = dp.combine_to_orders_table(people_df_op, objects_df_op)
    assert orders_df_op.is_ok(), "\n{}\n".format(orders_df_op)
    print(orders_df_op.ok)
    print(orders_df_op.ok.info())


# def test()
