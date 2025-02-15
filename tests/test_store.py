import pytest
from PySide6.QtCore import QUrl
import pandas as pd
from pathlib import Path
import tempfile
import os
from datetime import datetime, timezone

from banana_dispenser.store import OrderMngr
from banana_dispenser import qt_pd_model


@pytest.fixture
def sample_people_data():
    return pd.DataFrame({"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"]})


@pytest.fixture
def sample_objects_data():
    return pd.DataFrame(
        {
            "object": ["banana", "apple", "orange"],
            "people_id": [1, 2, 3],
            "pickup_datetime": [pd.NaT, pd.NaT, pd.NaT],
        }
    )


@pytest.fixture
def temp_csv_files(sample_people_data, sample_objects_data):
    with tempfile.TemporaryDirectory() as temp_dir:
        people_path = Path(temp_dir) / "people.csv"
        objects_path = Path(temp_dir) / "objects.csv"

        sample_people_data.to_csv(people_path, index=False)
        sample_objects_data.to_csv(objects_path, index=False)

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

    # Test pickup for person with ID 1
    success = order_manager.object_pick_up(1)
    assert success

    # Verify pickup time was set
    result_df = order_manager.ordersTableModel.df_data
    pickup_time = result_df[result_df["people_id"] == 1]["pickup_datetime"].iloc[0]
    assert not pd.isna(pickup_time)


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
