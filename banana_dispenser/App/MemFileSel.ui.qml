import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Controls.Material
import QtCore

Item {
    width: parent.width

    // height: 100

    property alias urlField: urlField.text
    property var settings

    Row {
        spacing: 10

        Label {
            text: "People list path:"
            anchors.verticalCenter: parent.verticalCenter
        }

        TextField {
            id: urlField

            width: 500
            height: 40
            anchors.verticalCenter: parent.verticalCenter
            placeholderText: StandardPaths.writableLocation(StandardPaths.DocumentsLocation) + "/people_list.csv"
            text: settings.people_list_url // init value only
            onEditingFinished: {
                if (!Util.if_file_uri_existed(urlField.text)) {
                    // if uri not existed
                    urlField.undo();
                    if (!Util.if_file_uri_existed(urlField.text)) {
                        // ori file not exist too
                        urlField.text = StandardPaths.writableLocation(StandardPaths.DocumentsLocation) + "/people_list.csv";
                    }
                }
                // else, success setting
            }
        }

        Button {
            text: qsTr("open file")
            onClicked: {
                Util.open_file_with_default_application(urlField.text);
            }
        }

        Button {
            text: qsTr("Select people list")
            onClicked: {
                fileDialog.selectedFile = urlField.text;
                if (!fileDialog.visible) {
                    fileDialog.open();
                }
            }
        }
    }

    FileDialog {
        id: fileDialog

        title: qsTr("Select a people list")
        nameFilters: ["list files (*.csv *.xls *.xlsx)"]
        onAccepted: {
            urlField.text = selectedFile;
            console.log("selected people list url:", urlField.text);
        }
        onRejected: {
            // Handle cancellation
            console.log("on reject called");
        }
        visible: false
    }
    implicitHeight: childrenRect.height + anchors.margins * 2
}
