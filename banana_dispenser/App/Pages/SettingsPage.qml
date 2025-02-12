import QtQuick
import QtCore //Settings
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Dialogs
import QtQuick.Layouts
import Store //OrderMngr

Page {
    property alias settings: settings

    title: qsTr("Settings")

    Settings {
        id: settings

        //RFC 1738
        property url peopleListUrl: peopleListPath.settingsUrl
        property url objectsListUrl: objectsListPath.settingsUrl

        onPeopleListUrlChanged: {
            OrderMngr.peopleListPath = peopleListUrl;
        }
        onObjectsListUrlChanged: {
            OrderMngr.objectListPath = objectsListUrl;
        }
    }

    Column {
        anchors.centerIn: parent
        anchors.fill: parent

        anchors.margins: 30
        spacing: 10

        MemFileSel {
            id: peopleListPath
            settingsUrl: settings.peopleListUrl
            memFiledName: "People list path"
        }
        MemFileSel {
            id: objectsListPath
            settingsUrl: settings.objectsListUrl
            memFiledName: "Object list path"
        }
    }
    //end of column
}
