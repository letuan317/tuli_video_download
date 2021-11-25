import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from termcolor import cprint
from urllib import request
import random


program_name = "Youtube Video Download"


class UIApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.window_width = 800
        self.window_height = 500

        self.setGeometry(80, 50, self.window_width, self.window_height)
        self.setMinimumSize(self.window_width, self.window_height)
        self.setWindowTitle(program_name)

        self.menuContainer = MenuObject(self)

        # Scroll Area which contains the widgets, set as the centralWidget

        self.setCentralWidget(self.menuContainer)

        self.statusbar = self.statusBar()
        self.statusBar().showMessage('Ready')

        self.show()


class MainWindow(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        formLayout = QFormLayout()
        groupBox = QGroupBox()

        for n in range(100):
            label1 = QLabel('Slime_%2d' % n)
            label2 = QLabel('Slime_%2d' % n)
            formLayout.addRow(label1, label2)

        groupBox.setLayout(formLayout)

        scroll = QScrollArea()
        scroll.setWidget(groupBox)
        scroll.setWidgetResizable(True)

        layout = QVBoxLayout(self)
        layout.addWidget(scroll)


class MenuObject(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.colorDarkGreen = "#264653"
        self.colorGreen = "#2a9d8f"
        self.colorGreenArmy = "#6b705c"
        self.colorYellow = "#e9c46a"
        self.colorOrange = "#f4a261"
        self.colorRed = "#e76f51"

        self.sizeMenuContainer = 100
        self.sizeMenuIcon = 48
        self.posXMenuIcon = 20
        self.posYMenuIcon = 20
        self.sizeFooterContainer = 20

        self.MenuContainer()
        self.test()

    def test(self):
        self.scroll = QScrollArea(self)
        self.widget = QWidget()
        self.vbox = QVBoxLayout()

        for i in range(1, 50):
            object = QLabel("TextLabel")
            self.vbox.addWidget(object)

        self.widget.setLayout(self.vbox)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

    def resizeEvent(self, event):
        window_size = self.geometry()
        self.window_width = window_size.width()
        self.window_height = window_size.height()

        self.menuBackground.setGeometry(
            0, 0, self.window_width, self.sizeMenuContainer)
        self.btnSetting.move(
            self.window_width - self.sizeMenuIcon - self.posXMenuIcon, self.posYMenuIcon)
        self.textSetting.move(
            self.window_width - self.sizeMenuIcon-17, self.posYMenuIcon+self.sizeMenuIcon+5)

        self.scroll.setGeometry(0, 110, 800, self.window_height-200)

    def MenuContainer(self):
        margin = 20

        self.menuBackground = QFrame(self)
        self.menuBackground.setStyleSheet(
            "QWidget { background-color: %s}" % self.colorDarkGreen)
        self.AddMenuButton("Paste", 10, 'img/icons8-plus-48.png',
                           self.posXMenuIcon, self.posYMenuIcon, self.ActionPasteLink)
        self.AddMenuButton("Add", 13, 'img/icons8-add-file-48.png',
                           self.posXMenuIcon+self.sizeMenuIcon+margin, self.posYMenuIcon, self.ActionAddFile)
        self.AddMenuButton("Download", 0, 'img/icons8-download-48.png',
                           self.posXMenuIcon+2*(self.sizeMenuIcon+margin), self.posYMenuIcon, self.ActionDownload)
        self.AddMenuButton("Pause", 8, 'img/icons8-pause-48.png',
                           self.posXMenuIcon+3*(self.sizeMenuIcon+margin), self.posYMenuIcon, self.ActionPause)
        self.AddMenuButton("Open", 8, 'img/icons8-folder-48.png',
                           self.posXMenuIcon+4*(self.sizeMenuIcon+margin), self.posYMenuIcon, self.ActionOpenFolder)
        self.AddMenuButton("Sort", 12, 'img/icons8-sort-48.png',
                           self.posXMenuIcon+5*(self.sizeMenuIcon+margin), self.posYMenuIcon, self.ActionSort)
        self.AddMenuButton("Clear", 10, 'img/icons8-clear-48.png',
                           self.posXMenuIcon+6*(self.sizeMenuIcon+margin), self.posYMenuIcon, self.ActionClear)

        self.btnSetting = QLabel(self)
        self.btnSetting.setPixmap(QPixmap("img/icons8-setting-48.png"))
        self.btnSetting.mousePressEvent = self.ActionSetting

        self.textSetting = QLabel("Settings", self)
        self.textSetting.setStyleSheet("QWidget { color: white}")

    def AddMenuButton(self, name, text_adjust, path_img, x, y, action):
        btnIconAddfile = QLabel(self)
        btnIconAddfile.setPixmap(QPixmap(path_img))
        btnIconAddfile.move(x, y)
        btnIconAddfile.mousePressEvent = action
        text = QLabel(name, self)
        text.move(x+text_adjust, y + self.sizeMenuIcon + 5)
        text.setStyleSheet("QWidget { color: white}")

    def ActionPasteLink(self, event):
        # TODO ActiocPasteLink: Paste a link from clipboard
        print('ActionPasteLink')

    def ActionAddFile(self, event):
        # TODO ActionAddFile: Read a file with youtube links and paste
        print('ActionAddFile')

    def ActionDownload(self, event):
        # TODO ActionDownload: Downloading
        print('ActionDownload')

    def ActionPause(self, event):
        # TODO ActionPause: Pause to download
        print('ActionPause')

    def ActionOpenFolder(self, event):
        # TODO ActionOpenFolder: Open video folder
        print('ActionOpenFolder')

    def ActionSort(self, event):
        # TODO ActionSort: Sort wait and downloaded
        print('ActionSort')

    def ActionClear(self, event):
        # TODO ActionClear: Delete video downloaded
        print('ActionClear')

    def ActionSetting(self, event):
        # TODO ActionSetting: Open Setting Panel
        print('ActionSetting')


def main():
    app = QApplication([])
    UI = UIApp()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
