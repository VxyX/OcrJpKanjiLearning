import typing
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
from PyQt5 import uic
from PyQt5.QtCore import Qt
import sys
from screen import ScreenShot
import os

################## Translate Menu ##################
class TranslatePage(QWidget):
    def __init__(self):
        super(TranslatePage, self).__init__()

        # load .ui file
        uic.loadUi("src/gui/mainuiWidget/TranslateWidget.ui", self)

        # 
        self.dicLang.setItemData(0, 'id')
        self.dicLang.setItemData(1, 'en')
        self.transLang.setItemData(0, 'id')
        self.transLang.setItemData(1, 'en')

        self.transLang.currentIndexChanged.connect(self.cekBahasaKamus)
        self.dicLang.setEnabled(False)
        self.checkDiffLang.stateChanged.connect(self.cekBahasaTerjemahan)
        self.startBtn.clicked.connect(self.startScreen)

    def startScreen(self):

        if not self.isStart:
            self.isStart = True
            self.screen = ScreenShot()
            self.startBtn.setText("Stop")
            
            print('click')
            # Thread(target=self.screen.show()).start()
            # Thread(target=self.textScreen.show()).start()
        else:
            self.isStart = False
            self.screen.closeScreen()
            self.startBtn.setText("Start")
            # Thread(target=self.screen.close()).start()
            # Thread(target=self.textScreen.close()).start()
            return
        
    def cekBahasaTerjemahan(self, state):
        if state == 2:  # Qt.Checked
            # print('Checkbox dicentang')
            self.dicLang.setEnabled(True)
        else:
            # print('Checkbox tidak dicentang')
            i = self.transLang.currentIndex()
            self.dicLang.setCurrentIndex(i)
            # print(i)
            self.dicLang.setEnabled(False)
    
    def cekBahasaKamus(self, index):
        # print(self.trasLang.currentData())
        if (self.checkDiffLang.checkState() == 0):
            self.dicLang.setCurrentIndex(index)
################## Translate Menu ##################

class BookmarkPage(QWidget):
    def __init__(self):
        super(BookmarkPage, self).__init__()

        # load .ui file
        uic.loadUi("src/gui/mainuiWidget/BookmarkWidget.ui", self)
        
class SettingsPage(QWidget):
    def __init__(self):
        super(SettingsPage, self).__init__()

        # load .ui file
        uic.loadUi("src/gui/mainuiWidget/SettingsWidget.ui", self)
        
class AboutPage(QWidget):
    def __init__(self):
        super(AboutPage, self).__init__()

        # load .ui file
        uic.loadUi("src/gui/mainuiWidget/InfoWidget.ui", self)

if __name__ == "__main__":
    print(os.getcwd())

        