from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic
import sys
from screen import ScreenShot, TextScreen

class Gui(QMainWindow):
    def __init__(self):
        super(Gui, self).__init__()

        # initialize
        self.isStart = False
        self.screen = None

        # load .ui file
        uic.loadUi("src/gui/mainui2.ui", self)

        # 
        self.dicLang.setItemData(0, 'id')
        self.dicLang.setItemData(1, 'en')
        self.transLang.setItemData(0, 'id')
        self.transLang.setItemData(1, 'en')

        self.transLang.currentIndexChanged.connect(self.checkTransLangIndexChange)
        self.dicLang.setEnabled(False)
        self.checkDiffLang.stateChanged.connect(self.checkDiffLangStateChange)
        self.startBtn.clicked.connect(self.startScreen)

        # show screen
        self.show()

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
        
    def checkDiffLangStateChange(self, state):
        if state == 2:  # Qt.Checked
            # print('Checkbox dicentang')
            self.dicLang.setEnabled(True)
        else:
            # print('Checkbox tidak dicentang')
            i = self.transLang.currentIndex()
            self.dicLang.setCurrentIndex(i)
            # print(i)
            self.dicLang.setEnabled(False)
    
    def checkTransLangIndexChange(self, index):
        # print(self.trasLang.currentData())
        if (self.checkDiffLang.checkState() == 0):
            self.dicLang.setCurrentIndex(index)
            


    
    
if (__name__ == "__main__"):
    app = QApplication(sys.argv)
    gui = Gui()
    app.exec_()