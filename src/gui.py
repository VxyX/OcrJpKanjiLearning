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
        uic.loadUi("src/gui/main.ui", self)

        # 
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
        
    
    
    
if (__name__ == "__main__"):
    app = QApplication(sys.argv)
    gui = Gui()
    app.exec_()