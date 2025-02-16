import pytest
import pandas as pd
import pytest
from unittest.mock import patch
from PySide6.QtCore import QUrl
import pandas as pd
from pathlib import Path
import tempfile
import os
from datetime import datetime, timezone

from banana_dispenser.store import OrderMngr
from banana_dispenser import qt_pd_model


@pytest.fixture
def sample_people_data() -> pd.DataFrame:
    """
    Fixture that provides a sample DataFrame with people's IDs and names.
    The 'id' column is set as the index.
    """
    data = {"id": [21, 1, 23], "name": ["Alice", "Bob", "Charlie"]}
    return pd.DataFrame(data).set_index("id")


@pytest.fixture
def sample_objects_data():
    return pd.DataFrame(
        {
            "id": [6, 8, 11],
            "object": ["banana", "apple", "orange"],
            "people_id": [1, 22, 23],
            "pickup_datetime": [pd.NaT, pd.NaT, pd.NaT],
        },
    ).set_index("id")


@pytest.fixture
def temp_csv_files(sample_people_data, sample_objects_data):
    with tempfile.TemporaryDirectory() as temp_dir:
        people_path = Path(temp_dir) / "people.csv"
        objects_path = Path(temp_dir) / "objects.csv"

        sample_people_data.to_csv(people_path, index=True)
        sample_objects_data.to_csv(objects_path, index=True)

        yield str(people_path), str(objects_path)


@pytest.fixture
def order_manager():
    return OrderMngr()


def test_initial_state(order_manager):
    assert order_manager.peopleListPath == QUrl()
    assert order_manager.objectListPath == QUrl()
    assert isinstance(order_manager.ordersTableModel, qt_pd_model.TableModel)
    assert order_manager.ordersTableModel.df_data.empty


def test_load_people_list(order_manager, temp_csv_files):
    people_path, _ = temp_csv_files
    order_manager.peopleListPath = QUrl.fromLocalFile(people_path)

    assert not order_manager._people_df.empty
    assert len(order_manager._people_df) == 3
    assert "name" in order_manager._people_df.columns


def test_load_objects_list(order_manager, temp_csv_files):
    _, objects_path = temp_csv_files
    order_manager.objectListPath = QUrl.fromLocalFile(objects_path)

    assert not order_manager._objects_df.empty
    assert len(order_manager._objects_df) == 3
    assert "object" in order_manager._objects_df.columns


def test_load_both_lists(order_manager, temp_csv_files):
    people_path, objects_path = temp_csv_files

    order_manager.peopleListPath = QUrl.fromLocalFile(people_path)
    order_manager.objectListPath = QUrl.fromLocalFile(objects_path)

    result_df = order_manager.ordersTableModel.df_data
    assert len(result_df) == 3
    print(result_df)
    assert all(
        col in result_df.columns
        for col in ["object", "people_id", "pickup_datetime", "name"]
    )


def test_object_pickup(order_manager, temp_csv_files):
    people_path, objects_path = temp_csv_files

    order_manager.peopleListPath = QUrl.fromLocalFile(people_path)
    order_manager.objectListPath = QUrl.fromLocalFile(objects_path)

    with patch.object(order_manager.ordersTableModel, "setData") as mock_setData:
        # with patch.object(TableModel, "setData") as mock_setData:

        # Test pickup for person with ID 1
        success = order_manager.object_pick_up(1)
        assert success

        # Verify pickup time was set
        result_df = order_manager.ordersTableModel.df_data
        pickup_time = result_df[result_df["people_id"] == 1]["pickup_datetime"].iloc[0]
        assert not pd.isna(pickup_time)

        # Verify that setData was called with the correct arguments
        mock_setData.assert_called()
        args, kwargs = mock_setData.call_args
        row = kwargs["index"].row()
        col = kwargs["index"].column()
        print("args:", args, kwargs)
        assert row == 0  # row index
        assert col == order_manager.ordersTableModel.df_data.columns.get_loc(
            "pickup_datetime"
        )
        assert not pd.isna(kwargs["value"])  # Ensure the pickup time is not NaT


def test_invalid_pickup(order_manager, temp_csv_files):
    people_path, objects_path = temp_csv_files

    order_manager.peopleListPath = QUrl.fromLocalFile(people_path)
    order_manager.objectListPath = QUrl.fromLocalFile(objects_path)

    # Test pickup for non-existent person
    success = order_manager.object_pick_up(999)
    assert not success


def test_double_pickup(order_manager, temp_csv_files):
    people_path, objects_path = temp_csv_files

    order_manager.peopleListPath = QUrl.fromLocalFile(people_path)
    order_manager.objectListPath = QUrl.fromLocalFile(objects_path)

    # First pickup should succeed
    first_pickup = order_manager.object_pick_up(1)
    assert first_pickup

    # Second pickup should still return True but not modify the pickup time
    second_pickup = order_manager.object_pick_up(1)
    assert second_pickup

    result_df = order_manager.ordersTableModel.df_data
    pickup_times = result_df[result_df["people_id"] == 1]["pickup_datetime"]
    assert len(pickup_times) == 1  # Should still only have one entry


def test_invalid_file_paths(order_manager):
    order_manager.peopleListPath = QUrl.fromLocalFile("nonexistent.csv")
    assert order_manager.ordersTableModel.df_data.empty

    order_manager.objectListPath = QUrl.fromLocalFile("nonexistent.csv")
    assert order_manager.ordersTableModel.df_data.empty
