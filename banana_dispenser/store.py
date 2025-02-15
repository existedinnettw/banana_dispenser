from PySide6 import QtCore
from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl
from PySide6.QtQml import QmlElement, QmlSingleton
from . import data_process as dp
from expression import Some, Result, Ok, Error
from . import qt_pd_model
import pandas as pd
from datetime import datetime, timezone
import os
import atexit
from .util import get_path_from_file_uri
import numpy as np

# register type to QML
QML_IMPORT_NAME = "Store"
QML_IMPORT_MAJOR_VERSION = 1


def _Qurl_touch_datetime(url: QUrl):
    return datetime.fromtimestamp(
        os.path.getmtime(get_path_from_file_uri(url.toString()))
    )


def _Qurl_to_path_str(url: QUrl):
    return str(get_path_from_file_uri(url.toString()))


@QmlElement
@QmlSingleton
class OrderMngr(QObject):
    ordersTableModelChanged = Signal(qt_pd_model.TableModel)
    peopleListPathChanged = Signal()
    objectListPathChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._people_list_path: QUrl = QUrl()
        self._objects_list_path: QUrl = QUrl()
        self._people_list_path_ori_touch_time: datetime = datetime.min
        self._objects_list_path_ori_touch_time: datetime = datetime.min
        self._objects_df: pd.DataFrame = pd.DataFrame()
        self._people_df: pd.DataFrame = pd.DataFrame()
        self._default_orders_table: pd.DataFrame = pd.DataFrame(
            columns=["object", "people_id", "pickup_datetime", "name"]
        )
        self._orders_table_model = qt_pd_model.TableModel(self._default_orders_table)

        atexit.register(self.__del__)

    @Property(QUrl, notify=peopleListPathChanged, final=True)
    def peopleListPath(self):
        return self._people_list_path

    @peopleListPath.setter
    def peopleListPath(self, url: QUrl) -> None:
        if url == self._people_list_path:
            return
        self._people_list_path = url
        self._update_people_df(url)

    @Property(QUrl, notify=objectListPathChanged, final=True)
    def objectListPath(self):
        return self._objects_list_path

    @objectListPath.setter
    def objectListPath(self, url: QUrl) -> None:
        if url == self._objects_list_path:
            return
        self._objects_list_path = url
        self._update_objects_df(url)

    @Property("QVariant", notify=ordersTableModelChanged, final=True)
    def ordersTableModel(self):
        return self._orders_table_model

    @ordersTableModel.setter
    def ordersTableModel(self, table_model: qt_pd_model.TableModel):
        self._orders_table_model.df_data = table_model.df_data
        self._orders_table_model.modelReset.emit()
        print("ordersTableModel updated.")

    @Slot(int, result=bool)
    def object_pick_up(self, people_id: int) -> bool:
        if people_id is None:
            return False

        orders_df = self._orders_table_model.df_data
        selected_rows = orders_df[orders_df["people_id"] == people_id]
        if selected_rows.empty:
            print("[DEBUG]: person doesn't order any object.")
            return False

        for id, row in selected_rows.iterrows():
            # id == row.name

            # find raw row index
            row_idx = np.where(orders_df.index == id)[0][0]  # is unique
            # # print("[DEBUG]\n", row_idx, "\n", id, "\n", row)

            if not pd.isna(row["pickup_datetime"]):
                print("[DEBUG]: person already picked up.")
                continue

            # update df
            now_time_pd_ts = pd.Timestamp(
                datetime.now(timezone.utc).replace(microsecond=0)
            ).tz_convert(tz="UTC")
            orders_df.at[id, "pickup_datetime"] = now_time_pd_ts

            # update object df
            self._objects_df.loc[
                self._objects_df.index == row.name, "pickup_datetime"
            ] = now_time_pd_ts

            # notify update qml
            column_idx = orders_df.columns.get_loc("pickup_datetime")
            # # print("[DEBUG] pick_up: row: ", row_idx, ", col: ", column_idx)
            self._orders_table_model.setData(
                index=self._orders_table_model.index(row_idx, column_idx),
                value=now_time_pd_ts,
            )

        return True

    def _update_people_df(self, url: QUrl):
        people_df_rst = Some(url.toString()).pipe(
            dp.open_list_file, dp.people_df_validator
        )
        if people_df_rst.is_error():
            self.ordersTableModel = qt_pd_model.TableModel(self._default_orders_table)
            return

        if not self._people_df.empty:
            dp.export_and_save_back_origin_path(
                self._people_df,
                _Qurl_to_path_str(self._people_list_path),
                self._people_list_path_ori_touch_time,
            )

        self._people_df = people_df_rst.ok
        self._people_list_path_ori_touch_time = _Qurl_touch_datetime(
            self._people_list_path
        )
        self._update_orders_table()

    def _update_objects_df(self, url: QUrl):
        objects_df_rst = Some(url.toString()).pipe(
            dp.open_list_file, dp.objects_df_validator
        )
        if objects_df_rst.is_error():
            self.ordersTableModel = qt_pd_model.TableModel(self._default_orders_table)
            return
        if not self._objects_df.empty:
            dp.export_and_save_back_origin_path(
                self._objects_df,
                _Qurl_to_path_str(self._objects_list_path),
                self._objects_list_path_ori_touch_time,
            )

        self._objects_df = objects_df_rst.ok
        self._objects_list_path_ori_touch_time = _Qurl_touch_datetime(
            self._objects_list_path
        )
        self._update_orders_table()

    def _update_orders_table(self):
        orders_df_rst = dp.combine_to_orders_table(
            Ok(self._people_df), Ok(self._objects_df)
        )
        if orders_df_rst.is_error():
            self.ordersTableModel = qt_pd_model.TableModel(self._default_orders_table)
            return
        self.ordersTableModel = qt_pd_model.TableModel(orders_df_rst.ok)

    def __del__(self):
        # print("[DEBUG] exit called")

        if not self._people_df.empty:
            dp.export_and_save_back_origin_path(
                self._people_df,
                _Qurl_to_path_str(self._people_list_path),
                self._people_list_path_ori_touch_time,
            )
            # print("[DEBUG] exported and saved people df.")
        if not self._objects_df.empty:
            # print(self._objects_df)
            dp.export_and_save_back_origin_path(
                self._objects_df,
                _Qurl_to_path_str(self._objects_list_path),
                self._objects_list_path_ori_touch_time,
            )
            # print("[DEBUG] exported and saved objects df.")
