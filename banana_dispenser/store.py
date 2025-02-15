from PySide6 import QtCore
from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl

# from PySide6.QtGui import QGuiApplication, QPen, QPainter, QColor
from PySide6.QtQml import QmlElement, QmlSingleton

from . import data_process as dp
from expression import Some, Result, Ok, Error
from . import qt_pd_model
import pandas as pd
import numpy as np
from datetime import datetime

# import copy

# register type to QML
QML_IMPORT_NAME = "Store"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
@QmlSingleton
class OrderMngr(QObject):

    ordersTableModelChanged = Signal(qt_pd_model.TableModel)

    # actually, will not change path by store own.
    peopleListPathChanged = Signal()
    objectListPathChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # as property or slot.
        # when path update, orders changed, too

        # manual init value is important
        self._people_list_path: QUrl = QUrl()
        self._objects_list_path: QUrl = QUrl()

        self._objects_df: pd.DataFrame = pd.DataFrame()  # imitate db table
        self._people_df: pd.DataFrame = pd.DataFrame()  # imitate db table

        # joined table, for display
        self._default_orders_table: pd.DataFrame = pd.DataFrame(
            data={
                # default value
                # "object": ["chocolate"],
                # "people_id": ["2"],
                # "pickup_datetime": [pd.NA],
                # "name": [],
            },
            columns=["object", "people_id", "pickup_datatime", "name"],
        )  # default
        self._orders_table_model = qt_pd_model.TableModel(self._default_orders_table)

    @Property(QUrl, notify=peopleListPathChanged, final=True)
    def peopleListPath(self):
        return self._people_list_path

    @peopleListPath.setter
    def peopleListPath(self, url: QUrl) -> None:
        # print(self)
        if url == self._people_list_path:
            return

        people_df_rst = Some(url.toString()).pipe(
            dp.open_list_file, dp.people_df_validator
        )
        self._people_list_path = url

        if people_df_rst.is_error():
            self.ordersTableModel = qt_pd_model.TableModel(self._default_orders_table)
            return
        self._people_df = people_df_rst.ok
        print("people df update")

        orders_df_rst = dp.combine_to_orders_table(people_df_rst, Ok(self._objects_df))

        if orders_df_rst.is_error():
            self.ordersTableModel = qt_pd_model.TableModel(self._default_orders_table)
            return

        self.ordersTableModel = qt_pd_model.TableModel(orders_df_rst.ok)

        print("ordersTableModel update with store people list path update")

    @Property(QUrl, notify=objectListPathChanged, final=True)
    def objectListPath(self):
        return self._objects_list_path

    @objectListPath.setter
    def objectListPath(self, url: QUrl) -> None:
        if url == self._objects_list_path:
            return
        self._objects_list_path = url

        # TODO better validator
        objects_df_rst = Some(url.toString()).pipe(
            dp.open_list_file, dp.objects_df_validator
        )
        if objects_df_rst.is_error():
            self.ordersTableModel = qt_pd_model.TableModel(self._default_orders_table)
            return
        self._objects_df = objects_df_rst.ok
        print("object df update")

        orders_df_rst = dp.combine_to_orders_table(Ok(self._people_df), objects_df_rst)

        if orders_df_rst.is_error():
            self.ordersTableModel = qt_pd_model.TableModel(self._default_orders_table)
            return

        self.ordersTableModel = qt_pd_model.TableModel(orders_df_rst.ok)
        # print(self.ordersTableModel.df_data)

        print("ordersTableModel update with store object list path update")

    # QML not support table model dtype
    # @Property("QVariant"

    @Property("QVariant", notify=ordersTableModelChanged, final=True)
    def ordersTableModel(self):
        # print(self._orders_table_model)
        print("pass table model")
        return self._orders_table_model

    @ordersTableModel.setter
    def ordersTableModel(self, table_model: qt_pd_model.TableModel):
        # variant

        # aware object my be shallow copy
        self._orders_table_model.df_data = table_model.df_data
        self._orders_table_model.modelReset.emit()  # model have its own special signal
        # self._orders_table_model = copy.copy(table_model) #no reducer
        print("ordersTableModel update.")

    # no setter need

    @Slot(int, result=bool)
    def object_pick_up(self, people_id: int) -> bool:
        """
        write pick_up time to specific record of underline file

        Returns
        -------
        success or fail
        """
        # find if object_id exist in df
        if people_id is None:
            return

        orders_df = self._orders_table_model.df_data
        selected_rows = orders_df[orders_df["people_id"] == people_id]
        if selected_rows.empty:
            print("[DEBUG]: person doesn't order any object.")
            return False

        # update value in df
        for row_idx, row in selected_rows.iterrows():
            row: pd.Series

            print(row["pickup_datetime"], type(row["pickup_datetime"]))
            if not row["pickup_datetime"] is pd.NaT:
                print("[DEBUG]: person already pick up.")
                break
            now_time_pd_ts = pd.Timestamp(
                datetime.today().replace(microsecond=0), tz="UTC"
            )
            orders_df.loc[orders_df.index == row_idx, "pickup_datetime"] = (
                now_time_pd_ts
            )
            # tz is forced to be compatible in type
            print(row_idx, "\n", row, "\n")

            # TODO how to show info on view
            column_idx = orders_df.columns.get_loc("pickup_datetime")

            self._orders_table_model.setData(
                index=self._orders_table_model.index(row_idx, column_idx),
                value=now_time_pd_ts,
            )
        print("[DEBUG] {} pick up object".format(selected_rows.head(1)["name"]))
        # print(orders_df)

        return True

    # # on app exit, export and save csv/excel config file
    # @Slot()
    # def export_updated_list() -> None:
    #     # check file timestamp, no-> save with conflict, yes -> save in same
    #     # name
    #     return
