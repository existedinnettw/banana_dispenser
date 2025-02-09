// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material

Page {

    width: 960
    height: 720

    SwipeView {
        id: swipeView

        width: parent.width
        height: parent.height
        currentIndex: tabBar.currentIndex

        ScanPage {
            id: scanPg
        }

        SettingsPage {
            id: settingsPg
        }

        // Ensures the focus changes to your page whenever you show a different page
        onCurrentItemChanged: {
            currentItem.forceActiveFocus();
        }
        Component.onCompleted: {
            currentItem.forceActiveFocus();
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

        currentIndex: swipeView.currentIndex

        TabButton {
            text: qsTr("Scan")
            onClicked: {
                tabBar.setCurrentIndex(0);
                console.log("Auto button clicked");
            }
        }

        TabButton {
            text: qsTr("Setting")
            onClicked: {
                tabBar.setCurrentIndex(1);
                console.log("Setting button clicked");
            }
        }
    }
    //end of footer
}
// end of page
