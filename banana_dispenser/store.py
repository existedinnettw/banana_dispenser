from PySide6 import QtCore
from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl
from PySide6.QtQml import QmlElement, QmlSingleton
from . import data_process as dp
from expression import Some, Result, Ok, Error
from . import qt_pd_model
import pandas as pd
from datetime import datetime

# register type to QML
QML_IMPORT_NAME = "Store"
QML_IMPORT_MAJOR_VERSION = 1


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
        self._objects_df: pd.DataFrame = pd.DataFrame()
        self._people_df: pd.DataFrame = pd.DataFrame()
        self._default_orders_table: pd.DataFrame = pd.DataFrame(
            columns=["object", "people_id", "pickup_datetime", "name"]
        )
        self._orders_table_model = qt_pd_model.TableModel(self._default_orders_table)

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

        for row_idx, row in selected_rows.iterrows():
            if not pd.isna(row["pickup_datetime"]):
                print("[DEBUG]: person already picked up.")
                continue
            now_time_pd_ts = pd.Timestamp(
                datetime.utcnow().replace(microsecond=0), tz="UTC"
            )
            orders_df.at[row_idx, "pickup_datetime"] = now_time_pd_ts
            column_idx = orders_df.columns.get_loc("pickup_datetime")
            self._orders_table_model.setData(
                index=self._orders_table_model.index(row_idx, column_idx),
                value=now_time_pd_ts,
            )
        print("[DEBUG] {} picked up object".format(selected_rows.head(1)["name"]))
        return True

    def _update_people_df(self, url: QUrl):
        people_df_rst = Some(url.toString()).pipe(
            dp.open_list_file, dp.people_df_validator
        )
        if people_df_rst.is_error():
            self.ordersTableModel = qt_pd_model.TableModel(self._default_orders_table)
            return
        self._people_df = people_df_rst.ok
        self._update_orders_table()

    def _update_objects_df(self, url: QUrl):
        objects_df_rst = Some(url.toString()).pipe(
            dp.open_list_file, dp.objects_df_validator
        )
        if objects_df_rst.is_error():
            self.ordersTableModel = qt_pd_model.TableModel(self._default_orders_table)
            return
        self._objects_df = objects_df_rst.ok
        self._update_orders_table()

    def _update_orders_table(self):
        orders_df_rst = dp.combine_to_orders_table(
            Ok(self._people_df), Ok(self._objects_df)
        )
        if orders_df_rst.is_error():
            self.ordersTableModel = qt_pd_model.TableModel(self._default_orders_table)
            return
        self.ordersTableModel = qt_pd_model.TableModel(orders_df_rst.ok)
