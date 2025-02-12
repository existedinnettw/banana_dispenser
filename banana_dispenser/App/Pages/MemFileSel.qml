import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Controls.Material
import QtCore
import Util

Item {
    id: memFileSel
    width: parent.width

    property string memFiledName
    property url settingsUrl //output current path to here

    QtObject {
        id: internal
        function convertString(inputString) {
            return inputString.toLowerCase().replace(/ /g, '_');
        }
        property url samplePath: StandardPaths.writableLocation(StandardPaths.DocumentsLocation) + "/" + internal.convertString(memFileSel.memFiledName) + ".sample.csv"
    }

    Row {
        spacing: 10

        Label {
            id: row_label
            text: memFileSel.memFiledName + ":"
            anchors.verticalCenter: parent.verticalCenter
        }

        TextField {
            id: urlField

            width: 500
            height: 40
            anchors.verticalCenter: parent.verticalCenter
            placeholderText: internal.samplePath
            inputMethodHints: Qt.ImhUrlCharactersOnly
            color: (memFileSel.settingsUrl.toString().length === 0) ? "grey" : "black"
            text: {
                // console.log(memFileSel.memFiledName, memFileSel.settingsUrl.toString(), memFileSel.settingsUrl.toString().length);
                if (memFileSel.settingsUrl.toString().length === 0)
                    return internal.samplePath.toString();
                else
                    return memFileSel.settingsUrl.toString();
            }
            onEditingFinished: {
                if (!Util.if_file_uri_existed(urlField.text)) {
                    // if uri not existed
                    urlField.text = internal.samplePath;
                    memFileSel.settingsUrl = "";
                } else {
                    memFileSel.settingsUrl = urlField.text;
                }
            }
        }
        Label {
            anchors.verticalCenter: parent.verticalCenter
            text: (memFileSel.settingsUrl.toString().length === 0) ? "❌" : "✔"
            color: (memFileSel.settingsUrl.toString().length === 0) ? "red" : "green"
            font.pointSize: 22
        }

        Button {
            text: qsTr("open file")
            onClicked: {
                Util.open_file_with_default_application(urlField.text);
            }
            enabled: (memFileSel.settingsUrl.toString().length === 0) ? false : true
        }

        Button {
            text: qsTr("Select file")
            onClicked: {
                fileDialog.selectedFile = (memFileSel.settingsUrl.toString().length === 0) ? Qt.resolvedUrl(".") : memFileSel.settingsUrl;
                if (!fileDialog.visible) {
                    fileDialog.open();
                }
            }
        }
    }

    FileDialog {
        id: fileDialog

        title: qsTr("Select a " + memFileSel.memFiledName.toLowerCase())
        nameFilters: ["list files (*.csv *.xls *.xlsx)"]
        onAccepted: {
            urlField.text = fileDialog.selectedFile;
            memFileSel.settingsUrl = urlField.text;
        }
        visible: false
    }
    implicitHeight: childrenRect.height + anchors.margins * 2
}
