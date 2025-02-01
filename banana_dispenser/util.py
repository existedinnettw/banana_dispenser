from PySide6.QtCore import QObject, Signal, Slot
from pathlib import Path
import os
import subprocess
import platform


def get_path_from_file_uri(uri: str) -> Path:
    """Return a new path from the given 'file' URI."""
    if not uri.startswith("file:"):
        raise ValueError(f"URI does not start with 'file:': {uri!r}")
    path = uri[5:]
    if path[:3] == "///":
        # Remove empty authority
        path = path[2:]
    elif path[:12] == "//localhost/":
        # Remove 'localhost' authority
        path = path[11:]
    if path[:3] == "///" or (path[:1] == "/" and path[2:3] in ":|"):
        # Remove slash before DOS device/UNC path
        path = path[1:]
    if path[1:2] == "|":
        # Replace bar with colon in DOS drive
        path = path[:1] + ":" + path[2:]
    from urllib.parse import unquote_to_bytes

    path_obj = Path(os.fsdecode(unquote_to_bytes(path)))
    if not path_obj.is_absolute():
        raise ValueError(f"URI is not absolute: {uri!r}")
    return path_obj


# slot func should always in class. therefore, to connect to qml, all thing should be in class
class Util(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(str, result=bool)
    def if_file_uri_existed(self, file_url: str) -> bool:
        p = Path()
        try:
            # p=Path.from_uri(file_url) #after python3.13
            p = get_path_from_file_uri(file_url)
        except Exception as e:
            print(e)
            return False

        if p.is_file():
            return True
        return False

    @Slot(str, result=None)
    def open_file_with_default_application(self, file_path: str) -> None:
        if platform.system() == "Darwin":  # macOS
            subprocess.call(("open", file_path))
        elif platform.system() == "Windows":  # Windows
            os.startfile(file_path)
        else:  # Linux variants
            subprocess.call(("xdg-open", file_path))
