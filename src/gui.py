import typing
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

        # load .ui file
        uic.loadUi("src/gui/mainui2.ui", self)

        self.mainPanel.insertWidget(0, menu.TranslatePage())
        self.mainPanel.insertWidget(1, menu.BookmarkPage())
        self.mainPanel.insertWidget(2, menu.SettingsPage())
        self.mainPanel.insertWidget(3, menu.AboutPage()) 

        self.translateBtn.clicked.connect(lambda: self.switchPage(0))
        self.bookmarkBtn.clicked.connect(lambda: self.switchPage(1))
        self.settingsBtn.clicked.connect(lambda: self.switchPage(2))
        self.aboutBtn.clicked.connect(lambda: self.switchPage(3))

        self.mainPanel.setCurrentIndex(0)

        # show screen
        self.show()

    def switchPage(self, index):
        self.mainPanel.setCurrentIndex(index)
        pass
################## Translate Menu ##################
    # call screen.py and textscreen.py
################## Translate Menu ##################

################## Bookmark Menu ##################
class BookmarkPage(QWidget):
    def __init__(self):
        super().__init__()
################## Bookmark Menu ##################

################## Pengaturan Menu ##################
class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
################## Pengaturan Menu ##################

################## Info App Menu ##################
class InfoAppPage(QWidget):
    def __init__(self):
        super().__init__()
################## Info App Menu ##################
            


    
    
if (__name__ == "__main__"):
    app = QApplication(sys.argv)
    gui = MainUi()
    app.exec_()