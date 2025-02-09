import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

Page {
    title: qsTr("Scan")

    Rectangle {
        id: root

        width: parent.width
        height: parent.height

        color: "transparent"
        Image {
            id: image
            width: 0.9 * parent.width
            height: 0.9 * parent.height

            fillMode: Image.PreserveAspectFit
            anchors.centerIn: root
            source: "qrc:/qt/qml/App/assets/banana.png"
            opacity: 0.5

            // NumberAnimation on opacity  {
            //     id: createAnimation
            //     from: 0
            //     to: 0.5
            //     duration: 500
            // }
        }

        Column {
            anchors.centerIn: parent
            anchors.fill: parent

            anchors.margins: 30
            spacing: 20

            Text {
                // width: parent.width
                font.pointSize: 21
                text: "Scaning RFID card..."
                anchors.horizontalCenter: parent.horizontalCenter
            }

            // hidden and monitor at background
            TextField {
                id: rfidTextField
                width: 400
                placeholderText: qsTr("Scaning RFID card input...")
                font.pointSize: 21
                font.bold: true
                anchors.horizontalCenter: parent.horizontalCenter
                focus: true
                // https://stackoverflow.com/a/76117389
                onFocusChanged: if (!focus)
                    Qt.callLater(forceActiveFocus)
            }

            Button {
                text: "Collect on behalf of"
                anchors.horizontalCenter: parent.horizontalCenter
                // form to fill target object, may need to filter order
                // onClicked: popup.open()
            }

            // tableView to display pd.Dataframe
            // may add `collect on behalf of` button for orders which is not pick up
            // sort by pick up time, and focus on not pickup yet orders.
            // search row feature
        }// end of column
    }
}

//end scan
