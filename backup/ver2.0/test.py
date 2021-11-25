import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from termcolor import cprint
from urllib import request
import random


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.colorDarkGreen = "#264653"
        self.colorGreen = "#2a9d8f"
        self.colorGreenArmy = "#6b705c"
        self.colorYellow = "#e9c46a"
        self.colorOrange = "#f4a261"
        self.colorRed = "#e76f51"

        self.window_width = 800
        self.window_height = 500

        self.sizeMenuContainer = 100
        self.sizeMenuIcon = 48
        self.posXMenuIcon = 20
        self.posYMenuIcon = 20
        self.sizeFooterContainer = 20

        self.initUI()

    def initUI(self):
        # Scroll Area which contains the widgets, set as the centralWidget
        self.scroll = QScrollArea()
        # Widget that contains the collection of Vertical Box
        self.widget = QWidget()
        # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        self.vbox = QVBoxLayout()

        self.menuBackground = QFrame(self)
        self.menuBackground.setStyleSheet(
            "QWidget { background-color: %s}" % self.colorDarkGreen)
        self.menuBackground.setGeometry(
            0, 0, self.window_width, self.sizeMenuContainer)

        self.AddMenuButton("Paste", 10, 'img/icons8-plus-48.png',
                           self.posXMenuIcon, self.posYMenuIcon, self.ActionPasteLink)

        for i in range(1, 50):
            object = QLabel("TextLabel")
            self.vbox.addWidget(object)

        self.widget.setLayout(self.vbox)

        # Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)

        self.setGeometry(600, 100, 1000, 900)
        self.setWindowTitle('Scroll Area Demonstration')
        self.show()

        return

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


def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
