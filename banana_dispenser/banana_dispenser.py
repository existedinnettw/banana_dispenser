import sys
import os
import urllib.request
import json
from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QStringListModel
from PySide6.QtGui import QGuiApplication

from .util import Util


def program():

    # Set up the application window
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("banana_dispenser")
    # app.setOrganizationDomain()
    # QQmlApplicationEngine
    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)

    # inject python object to qml
    util = Util()
    view.engine().rootContext().setContextProperty("Util", util)

    # Load the QML file
    # Dynamically add the import path
    # [examples/graphs/3d/bars/main.py](https://github.com/qtproject/pyside-pyside-setup/blob/23b7ff61fb899ef8ae305df134d2c0968dce1fa2/examples/graphs/3d/bars/main.py#L16)
    import_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, import_path)
    # print("[debug] add import path: {}".format(import_path))
    view.engine().addImportPath(import_path)
    view.loadFromModule("App", "Main")  # uri, typename

    # Show the window
    if view.status() == QQuickView.Error:
        sys.exit(-1)
    view.show()

    # execute and cleanup
    app.exec()
    del view


if __name__ == "__main__":
    program()
