from PySide6 import QtCore
from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl

# from PySide6.QtGui import QGuiApplication, QPen, QPainter, QColor
from PySide6.QtQml import QmlElement, QmlSingleton

from . import data_process as dp
from expression import Some
from . import qt_pd_model
import pandas as pd

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

        people_df_op = Some(url.toString()).pipe(dp.open_list_file)
        # objects_df_op = Some(sel).pipe(open_list_file)
        if people_df_op.is_none():
            return
        self._people_list_path = url
        self._people_df = people_df_op.value
        self.peopleListPathChanged.emit()
        print("people df update")

        orders_df_op = dp.combine_to_orders_table(people_df_op, Some(self._objects_df))

        if orders_df_op.is_none():
            self.ordersTableModel = qt_pd_model.TableModel(self._default_orders_table)
            return

        self.ordersTableModel = qt_pd_model.TableModel(orders_df_op.value)

        print("ordersTableModel update with store people list path update")

    @Property(QUrl, notify=objectListPathChanged, final=True)
    def objectListPath(self):
        return self._objects_list_path

    @objectListPath.setter
    def objectListPath(self, url: QUrl):
        if url == self._objects_list_path:
            return

        # people_df_op = Some(self._people_list_path.toString()).pipe(dp.open_list_file)
        objects_df_op = Some(url.toString()).pipe(dp.open_list_file)
        if objects_df_op.is_none():
            return
        self._objects_list_path = url
        self._objects_df = objects_df_op.value
        self.objectListPathChanged.emit()
        print("object df update")

        orders_df_op = dp.combine_to_orders_table(Some(self._people_df), objects_df_op)

        if orders_df_op.is_none():
            self.ordersTableModel = qt_pd_model.TableModel(self._default_orders_table)
            return

        self.ordersTableModel = qt_pd_model.TableModel(orders_df_op.value)
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
        # self.ordersTableModelChanged.emit(self._orders_table_model)
        self._orders_table_model.modelReset.emit()  # model have its own special signal
        # self._orders_table_model = copy.copy(table_model) #no reducer
        print("ordersTableModel update.")

    # no setter need

    # @Slot(int, result=bool)
    # def object_pick_up(self, object_id: int) -> bool:
    #     """
    #     write pick_up time to specific record of underline file

    #     Returns
    #     -------
    #     success or fail
    #     """
    #     # open file
    #     # find specific line of file
    #     # update value in file

    #     return True

    # # on app exit, export and save csv/excel config file
    # @Slot()
    # def export_updated_list() -> None:
    #     # check file timestamp, no-> save with conflict, yes -> save in same
    #     # name
    #     return
