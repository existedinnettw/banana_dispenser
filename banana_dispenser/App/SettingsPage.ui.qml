import QtQuick
import QtCore //Settings
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Dialogs
import QtQuick.Layouts

Item {
    Settings {
        id: settings

        //RFC 1738
        property url people_list_url: StandardPaths.writableLocation(StandardPaths.DocumentsLocation) + "/people_list.csv"
        property url mqtt_broker_url: "tcp://localhost:1883"
        property double feed_rate: 0.5
        property string machine_id: "1"
    }

    Component.onDestruction: function () {
        settings.people_list_url = urlField.text;
        settings.feed_rate = slide.value;
        settings.mqtt_broker_url = brokerUrlField.text;
        settings.machine_id = machineIdField.text;
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

        Row {
            spacing: 10

            Label {

                // verticalAlignment: Text.AlignVCenter
                // font.pixelSize:

                text: "Mqtt broker URL:"
                anchors.verticalCenter: parent.verticalCenter
            }

            TextField {
                id: brokerUrlField

                width: 280
                height: 40
                placeholderText: "tcp://localhost:1883"
                text: settings.mqtt_broker_url //init value only
            }
        }

        Row {
            spacing: 10

            Label {

                // verticalAlignment: Text.AlignVCenter
                // font.pixelSize:

                text: "machine id:"
                anchors.verticalCenter: parent.verticalCenter
            }

            TextField {
                id: machineIdField

                width: 280
                height: 40
                placeholderText: "1"
                text: settings.machine_id //init value only
            }
        }

        Row {
            spacing: 10

            Label {
                text: "feed rate(m/s):"
                anchors.verticalCenter: parent.verticalCenter
            }

            Slider {
                // moved:
                id: slide

                from: 0.1
                value: settings.feed_rate //init value only
                to: 1.1
                stepSize: 0.1
                snapMode: Slider.SnapAlways

                Text {
                    text: "slow"
                    anchors.top: slide.bottom
                    anchors.left: slide.left
                }

                Text {
                    text: "fast"
                    anchors.top: slide.bottom
                    anchors.right: slide.right
                }
            }

            Text {
                // anchors.top: slide.bottom
                // anchors.left: 0.5 * (slide.left + slide.right)
                anchors.verticalCenter: parent.verticalCenter
                text: slide.value.toFixed(1)
            }
        }
    }
    //end of column
}
