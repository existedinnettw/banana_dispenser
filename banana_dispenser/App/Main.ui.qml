// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material

Page {
    required property var myModel

    width: 960
    height: 720

    StackLayout {
        width: parent.width
        height: parent.height
        currentIndex: tabBar.currentIndex

        Rectangle {
            id: root

            width: parent.width
            height: parent.height

            Image {
                id: image
                width: 666
                height: 594

                fillMode: Image.PreserveAspectFit
                anchors.centerIn: root
                source: "./logo.png"
                opacity: 0.5
            }

            ListView {
                id: view

                anchors.fill: root
                anchors.margins: 25
                model: myModel

                delegate: Text {
                    anchors.leftMargin: 50
                    font.pointSize: 15
                    horizontalAlignment: Text.AlignHCenter
                    text: display
                }
            }
        }

        NumberAnimation {
            id: anim

            running: true
            target: view
            property: "contentY"
            duration: 500
        }
    }

    //end StackLayout

    header: Label {
        color: "#15af15"
        text: qsTr("Banana dispenser")
        font.pointSize: 17
        font.bold: true
        font.family: "Arial"
        renderType: Text.NativeRendering
        horizontalAlignment: Text.AlignHCenter
        padding: 10
    }

    // end of header

    footer: TabBar {
        id: tabBar

        currentIndex: 0

        TabButton {
            text: qsTr("Scan")
            onClicked: console.log("Auto button clicked")
        }

        TabButton {
            text: qsTr("Setting")
            onClicked: console.log("Setting button clicked")
        }
    }
    //end of footer
}
// end of page
