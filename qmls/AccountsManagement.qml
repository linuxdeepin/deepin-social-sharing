import QtQuick 2.1
import QtGraphicalEffects 1.0
import Deepin.Widgets 1.0

SlideInOutItem {
    id: root

    property var parentWindow

    signal login(string type)

    function addUser(accountType, uid, username) {
        var index = 0
        switch (accountType) {
            case "sinaweibo": {
                index = 0
                break
            }
            case "twitter": {
                index = 1
                break
            }
        }
        var _accounts = list_view.model.get(index).accounts
        var result = []
        if (_accounts) {
            result = JSON.parse(_accounts)
        }
        result.push({
            "username": username,
            "uid": uid
            })
        list_view.model.setProperty(index, "accounts", JSON.stringify(result))
    }

    ListView {
        id: list_view
        width: parent.width
        height: parent.height

        highlight: Rectangle {
            clip: true

            RadialGradient {
                width: parent.width
                height: parent.height + 20
                verticalOffset: - height / 2

                gradient: Gradient {
                    GradientStop { position: 0.0; color: Qt.rgba(0, 0, 0, 0.3) }
                    GradientStop { position: 1.0; color: Qt.rgba(0, 0, 0, 0.0) }
                }
            }
        }
        delegate: Item {
            id: delegate_item
            width: ListView.view.width
            height: 38

            Row {
                id: row
                width: account_icon.width + combobox.width
                height: Math.max(account_icon.implicitHeight, combobox.height)
                spacing: 10

                anchors.centerIn: parent

                Image {
                    id: account_icon
                    source: iconSource

                    anchors.verticalCenter: parent.verticalCenter
                }

                DComboBox {
                    id: combobox
                    width: 120
                    visible: accounts != ""
                    parentWindow: root.parentWindow
                    selectIndex: 0
                    menu.labels: {
                        var result = []
                        if (accounts) {
                            var _accounts = JSON.parse(accounts)
                            for (var i = 0; i < _accounts.length; i++) {
                                result.push(_accounts[i].username)
                            }
                        } else {
                            result = [""]
                        }
                        return result
                    }

                    anchors.verticalCenter: parent.verticalCenter
                }

                DTextButton {
                    text: "Login"
                    visible: accounts == ""

                    anchors.verticalCenter: parent.verticalCenter

                    onClicked: root.login(accountType)
                }
            }

            MouseArea {
                hoverEnabled: true
                anchors.fill: parent

                onPressed: mouse.accepted = false
                onReleased: mouse.accepted = false
                onEntered: delegate_item.ListView.view.currentIndex = index
                onExited: delegate_item.ListView.view.currentIndex = -1
            }
        }
        model: ListModel{
            ListElement {
                iconSource: "../images/sinaweibo_big.png"
                accountType: "sinaweibo"
                accounts: ""
            }
            ListElement {
                iconSource: "../images/twitter_big.png"
                accountType: "twitter"
                accounts: ""
            }
        }
    }
}