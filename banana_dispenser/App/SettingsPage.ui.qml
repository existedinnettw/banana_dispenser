import QtQuick
import QtCore //Settings
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Dialogs
import QtQuick.Layouts

Page {
    property alias settings: settings

    title: qsTr("Settings")

    Settings {
        id: settings

        //RFC 1738
        property url people_list_url: StandardPaths.writableLocation(StandardPaths.DocumentsLocation) + "/people_list.csv"
    }

    Component.onDestruction: function () {
        settings.people_list_url = peopleListPath.urlField;
    }

    Column {
        anchors.centerIn: parent
        anchors.fill: parent

        anchors.margins: 30
        spacing: 10

        MemFileSel {
            id: peopleListPath
            settings: settings
        }
    }
    //end of column
}
