import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from termcolor import cprint
from urllib import request

program_name = "Youtube Video Download"


class UIApp(QWidget):
    def __init__(self):
        super().__init__()
        self.window_width = 800
        self.window_height = 500

        self.setGeometry(0, 0, self.window_width, self.window_height)
        self.setMinimumSize(self.window_width, self.window_height)
        self.setWindowTitle(program_name)

        self.colorDarkGreen = "#264653"
        self.colorGreen = "#2a9d8f"
        self.colorYellow = "#e9c46a"
        self.colorOrange = "#f4a261"
        self.colorRed = "#e76f51"

        self.sizeMenuContainer = 100
        self.sizeMenuIcon = 48
        self.posXMenuIcon = 20
        self.posYMenuIcon = 20
        self.sizeFooterContainer = 20

        self.sizeVideoContainer = 100

        self.MenuContainer()
        self.VideoContainer(x=800,
                            y=110, url_image='https://live.staticflickr.com/65535/49251422908_591245c64a_c_d.jpg',
                            title="12345678901234567890123456789012345678901234567890123456789012345678901234567890",
                            channel="12345678901234567890", formats=["01", "02", "03", "04"], status="Wait")

        self.Footer("Ready")

        self.show()

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

    def resizeEvent(self, event):
        window_size = self.geometry()
        self.window_width = window_size.width()
        self.window_height = window_size.height()
        cprint((self.window_width, self.window_height), "yellow")

        self.menuBackground.setGeometry(
            0, 0, self.window_width, self.sizeMenuContainer)
        self.btnSetting.move(
            self.window_width - self.sizeMenuIcon - self.posXMenuIcon, self.posYMenuIcon)
        self.textSetting.move(
            self.window_width - self.sizeMenuIcon-17, self.posYMenuIcon+self.sizeMenuIcon+5)

        self.footerBackground.setGeometry(
            0, self.window_height-self.sizeFooterContainer, self.window_width, self.sizeFooterContainer)
        self.footerMessage.move(
            5, self.window_height-self.sizeFooterContainer+1)

    def VideoContainer(self, x, y, url_image, title, channel, formats, status):
        print("test", x)
        videoBackground = QFrame(self)
        videoBackground.setStyleSheet(
            "QWidget { border-radius: 5px; background-color: %s}" % self.colorGreen)
        #videoBackground.setGeometry(0, y, 800, 100)
        videoBackground.setMinimumSize(QSize(800, 100))
        videoBackground.setSizePolicy(QSizePolicy.Fixed, 100)
        videoBackground.move(0, y)

        data = request.urlopen(url_image).read()

        pixmap = QPixmap()
        pixmap.loadFromData(data)
        #pixmap.scaled(100, 80, Qt.IgnoreAspectRatio, Qt.FastTransformation)
        pixmap = pixmap.scaledToWidth(100)
        pixmap = pixmap.scaledToHeight(90)
        thumbnail = QLabel(self)
        thumbnail.setPixmap(pixmap)
        thumbnail.move(5, y+5)

        title = QLabel(title, self)
        title.setStyleSheet(
            "QWidget { color: white; font-size: 15px; font-weight: bold; background: red}")
        title.setGeometry(175, y + 5, self.window_width-200, 50)

        channel = QLabel(channel, self)
        channel.setStyleSheet(
            "QWidget { color: white;}")
        channel.move(175, y + 75)

        combo_box = QComboBox(self)
        for ft in formats:
            combo_box.addItem(ft)
        combo_box.setGeometry(350, y + 75, 300, 20)

        channel = QLabel(status, self)
        channel.setStyleSheet(
            "QWidget { color: white; font-size: 15px; font-weight: bold}")
        channel.move(self.window_width-100, y + 75)

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

    def Footer(self, text):
        self.footerBackground = QFrame(self)
        self.footerBackground.setStyleSheet(
            "QWidget { background-color: %s}" % self.colorDarkGreen)
        self.footerMessage = QLabel(text, self)
        self.footerMessage.setStyleSheet("QWidget { color: white}")


def main():
    app = QApplication(sys.argv)
    ex = UIApp()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
