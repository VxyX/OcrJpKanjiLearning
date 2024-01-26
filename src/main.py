import typing
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
from PyQt5 import QtCore, uic
import sys

import menu

class MainUi(QMainWindow):
    def __init__(self):
        super().__init__()

        # initialize
        self.isStart = False
        self.screen = None
        self.bmIsShow = False

        # load .ui file
        uic.loadUi("src/gui/mainui2.ui", self)

        self.setWindowTitle("JP OCR Translation")

        self.bmPage = menu.BookmarkPage()
        self.tlPage = menu.TranslatePage(self.bmPage)
        self.abPage = menu.AboutPage()

        self.mainPanel.insertWidget(0, self.tlPage)
        self.mainPanel.insertWidget(1, self.abPage) 

        self.translateBtn.clicked.connect(lambda: self.switchPage(0))
        self.bookmarkBtn.clicked.connect(self.bookmarkBtnEv)
        self.aboutBtn.clicked.connect(lambda: self.switchPage(1))

        self.mainPanel.setCurrentIndex(0)

        # show screen
        self.show()

    def switchPage(self, index):
        self.mainPanel.setCurrentIndex(index)
        pass

    def bookmarkBtnEv(self):
        if self.bmPage.isShown:
            pass
        else:
            self.bmPage.show()
            self.bmPage.isShown = True
        pass

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.bmPage.close()
        self.tlPage.close()
        return super().closeEvent(a0)

            


    
    
if (__name__ == "__main__"):
    app = QApplication(sys.argv)
    gui = MainUi()
    app.exec_()