from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl

# from PySide6.QtGui import QGuiApplication, QPen, QPainter, QColor
from PySide6.QtQml import QmlElement

from . import data_process as dp
import pandas as pd

# register type to QML
QML_IMPORT_NAME = "Store"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class OrderMngr(QObject):

    orderChanged = Signal()

    peopleListPathChanged = Signal()
    objectListPathChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # as property or slot.
        # when path update, orders changed, too
        self._people_list_path: QUrl
        self._objects_list_path: QUrl

        self._orders_table: pd.DataFrame  # joined table, for display
        self._people_df: pd.DataFrame  # imitate db table
        self._objects_df: pd.DataFrame  # imitate db table

    @Property(QUrl, notify=orderChanged, final=True)
    def peopleListPath(self):
        return self._people_list_path

    @peopleListPath.setter
    def peopleListPath(self, url: QUrl):
        self._people_list_path = url

    @Property(QUrl, notify=objectListPathChanged, final=True)
    def objectListPath(self):
        return self._objects_list_path

    @objectListPath.setter
    def objectListPath(self, url: QUrl):
        self._objects_list_path = url
        # update orders df

    @Slot(int, result=bool)
    def object_pick_up(self, object_id: int) -> bool:
        """
        write pick_up time to specific record of underline file

        Returns
        -------
        success or fail
        """
        # open file
        # find specific line of file
        # update value in file

        return True

    # on app exit, export and save csv/excel config file
    @Slot()
    def export_updated_list() -> None:
        # check file timestamp, no-> save with conflict, yes -> save in same
        # name
        return
