import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from termcolor import cprint

program_name = "Youtube Video Download"


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.MenuContainer()
        self.setGeometry(100, 100, 500, 300)
        self.setMinimumSize(500, 300)
        self.setWindowTitle(program_name)
        self.show()

    def MenuContainer(self):
        init_x = 10
        init_y = 10
        img_width = 48
        margin = 10
        self.test = 0
        self.AddButton('img/icons8-plus-48.png',
                       init_x, init_y, self.ActionAddFile)
        self.AddButton('img/icons8-add-file-48.png',
                       init_x+img_width+margin, init_y, self.ActionAddFile)
        self.AddButton('img/icons8-download-48.png',
                       init_x+2*(img_width+margin), init_y, self.ActionAddFile)
        self.AddButton('img/icons8-pause-48.png',
                       init_x+3*(img_width+margin), init_y, self.ActionAddFile)
        self.AddButton('img/icons8-sort-48.png',
                       init_x+4*(img_width+margin), init_y, self.ActionAddFile)
        self.AddButton('img/icons8-delete-48.png',
                       init_x+5*(img_width+margin),
                       init_y, self.ActionAddFile)
        self.AddButton('img/icons8-setting-48.png',
                       self.test,
                       10, self.ActionAddFile)

    def resizeEvent(self, event):
        size = self.geometry()
        print(size.width())
        self.test += 10

    def AddButton(self, path_img, x, y, action):
        btnIconAddfile = QLabel(self)
        btnIconAddfile.setPixmap(QPixmap(path_img))
        btnIconAddfile.move(x, y)
        btnIconAddfile.mousePressEvent = action

    def ActionAddFile(self, event):
        print('ActionAddFile')
        size = self.geometry()
        print(size.width())

    def Footer(self):
        self.statusBar().showMessage('Ready')


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
