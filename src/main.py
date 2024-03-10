from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic
import sys

import menu

class MainUi(QMainWindow):
    def __init__(self):
        super().__init__()

        # initialize
        self.isStart = False
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
            self.bmPage.isActive = True
            self.bmPage.mainAppRun = True
            self.isShown = True
        pass

    def closeEvent(self, a0: QCloseEvent) -> None:
        if self.bmPage.isActive:
            self.bmPage.mainAppRun = False
            self.bmPage.close()
        self.tlPage.close()
        return super().closeEvent(a0)

            


    
    
if (__name__ == "__main__"):
    print(__name__)
    import logging
    import datetime
    logging.basicConfig(filename='err.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.WARNING)
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)
    now = datetime.datetime.now()
    # print(now.strftime("%Y-%m-%d %H:%M:%S"))
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        with open("err.log", 'a') as my_file:
            my_file.write('\n\n')

    sys.excepthook = handle_exception
    app = QApplication(sys.argv)
    gui = MainUi()
    # gui[0]=0
    app.exec_()