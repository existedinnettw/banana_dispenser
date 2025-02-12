import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt.labs.qmlmodels
import Store //OrderMngr

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
        // ColumnLayout{
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
                // onFocusChanged: if (!focus)
                //     Qt.callLater(forceActiveFocus)
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
            Item {
                id: ordersTableFrame
                width: 0.8 * parent.width
                // height: 0.8 * parent.height
                // height: 100
                height: parent.height- y
                // Layout.fillHeight: true //fill rest of Column

                anchors.horizontalCenter: parent.horizontalCenter

                HorizontalHeaderView {
                    id: horizontalHeader
                    anchors {
                        left: ordersTableView.left
                        top: parent.top
                        topMargin: 1
                    }
                    syncView: ordersTableView
                    clip: true

                    // QML table view not correctly impl `headerData` yet
                    // model: ["name","color"] //modelData ver
                                        
                    delegate: Rectangle {
                        implicitWidth: 150
                        implicitHeight: 30
                        opacity:0.8
                        color: "gray"

                        Text {
                            text: model.display
                            font.pointSize: 14

                            // text: modelData
                            anchors.centerIn: parent
                        }
                    }
                }
                // VerticalHeaderView {
                //     id: tableViewVerticalHeader
                //     // anchors.top: ordersTableViewtop
                //     // anchors.left: parent.left
                //     anchors {
                //         top: ordersTableView.top
                //         left: parent.left
                //         leftMargin: 1
                //     }
                //     syncView: ordersTableView
                //     clip: true
                // }
                TableView {
                    id : ordersTableView
                    // anchors.fill: parent
                    anchors.top : horizontalHeader.bottom
                    anchors.topMargin : 6
                    width: parent.width
                    height: parent.height

                    anchors.horizontalCenter: parent.horizontalCenter

                    columnSpacing: 3
                    rowSpacing: 3
                    
                    clip: true

                    // model: ordersTableFrame.exampleModel
                    model: OrderMngr.ordersTableModel

                    selectionModel: ItemSelectionModel {}

                    // columnWidthProvider: function (column) { return column === 0 ? width : 0 }
                    // onWidthChanged: forceLayout()

                    //each cell
                    delegate: Rectangle {
                        // implicitWidth: 150
                        // implicitWidth: TableView.view.width
                        implicitWidth: Math.max(cellText.implicitWidth+18, 150)
                        implicitHeight: 50
                        // implicitHeight: Math.max(cellText.implicitHeight)
                        opacity:0.8
                        anchors.margins:2

                        Text {
                            id: cellText
                            text: display
                            anchors.centerIn: parent
                        }
                        
                        //edit cell
                        TableView.editDelegate: TextField {
                            anchors.fill: parent
                            text: display
                            horizontalAlignment: TextInput.AlignHCenter
                            verticalAlignment: TextInput.AlignVCenter

                            Component.onCompleted: selectAll()

                            TableView.onCommit: {
                                display = text
                                // 'display = text' is short-hand for:
                                // let index = TableView.view.index(row, column)
                                // TableView.view.model.setData(index, "display", text)
                            }
                        }
                    } //end of cell delegate
                    ScrollBar.vertical: ScrollBar {}
                    ScrollBar.horizontal: ScrollBar {}
                }//end of  TableView
            }//end of Item
        }// end of column
    }
}

//end scan
