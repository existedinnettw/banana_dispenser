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
        property url people_list_url: peopleListPath.settingsUrl
        property url objects_list_url: objectsListPath.settingsUrl
    }

    // Component.onDestruction: function () {
    //     settings.people_list_url = peopleListPath.urlField;
    // }

    Column {
        anchors.centerIn: parent
        anchors.fill: parent

        anchors.margins: 30
        spacing: 10

        MemFileSel {
            id: peopleListPath
            settingsUrl: settings.people_list_url
            memFiledName: "People list path"
        }
        MemFileSel {
            id: objectsListPath
            settingsUrl: settings.objects_list_url
            memFiledName: "Object list path"
        }
    }
    //end of column
}
