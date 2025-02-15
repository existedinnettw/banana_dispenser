import sys
from PySide6 import QtCore  # ,QtGui, QtWidgets
from PySide6.QtCore import Qt

import pandas as pd
import builtins
from typing import Type
from datetime import datetime


class TableModel(QtCore.QAbstractTableModel):
    # https://www.pythonguis.com/tutorials/pyside6-qtableview-modelviews-numpy-pandas/#pandas

    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self.df_data: pd.DataFrame = data  # .copy()

    def data(self, index, role):
        match role:
            # https://doc.qt.io/qt-6/qabstractitemmodel.html#roleNames
            # case Qt.DisplayRole | Qt.EditRole:

            case _:
                # print("data: ", "row: ", index.row(), "col: ", index.column())
                value = self.df_data.iloc[index.row(), index.column()]
                match type(value):
                    case pd.Timestamp:
                        return (
                            value.to_pydatetime()
                            .astimezone()
                            .replace(tzinfo=None)
                            .isoformat()
                        )
                    case _:
                        return str(value)

    def rowCount(self, index):
        return self.df_data.shape[0]

    def columnCount(self, index):
        return self.df_data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                # print(self.df_data.columns[section])
                return str(self.df_data.columns[section]).replace("_", " ")

            if orientation == Qt.Vertical:
                return str(self.df_data.index[section])

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        """
        Returns true if successful; otherwise returns false.
        The dataChanged() signal should be emitted if the data was successfully set.

        """
        # row = index.row()
        # col = index.column()
        # print("[DEBUG] setData called")
        # print("row: ", row, ", col: ", col)
        # print(self.df_data)

        self.dataChanged.emit(index, index)

        return True

    def flags(self, index):
        """Set the item flags at the given index. Seems like we're
        implementing this function just to see how it's done, as we
        manually adjust each tableView to have NoEditTriggers.
        """
        if not index.isValid():
            return Qt.ItemFlag.ItemIsEnabled
        return Qt.ItemFlags(
            QtCore.QAbstractTableModel.flags(self, index)
            | Qt.ItemFlag.ItemIsEditable  # let cell editable
        )
