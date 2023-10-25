import typing
import pyautogui
import time
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QGraphicsOpacityEffect, QSizeGrip
from PyQt5 import QtGui, uic
from PyQt5.QtCore import Qt, QPoint, QRect
import sys

from txtscreen import TextScreen

from pprint import pprint

class ScreenShot(QMainWindow):
    def __init__(self):
        super(ScreenShot, self).__init__()

        # load file
        self.uifile = "src/gui/screenCapture copy.ui"
        self.stylefile = "src/style/screenshot.qss"

        uic.loadUi(self.uifile, self)
        with open(self.stylefile,"r") as fh:
            self.setStyleSheet(fh.read())

        self.textScreen = TextScreen()

        # set transparancy
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWinOpacity = 1
        self.setWindowOpacity(self.setWinOpacity)
        self.takingss = False
        # self.op=QGraphicsOpacityEffect(self.centralwidget)
        # self.op.setOpacity(self.setWinOpacity)
        # self.centralwidget.setGraphicsEffect(self.op)
        # self.centralwidget.setAutoFillBackground(True)

        # set grip
        self.leftGrip.setCursor(Qt.SizeHorCursor)
        self.rightGrip.setCursor(Qt.SizeHorCursor)
        self.topGrip.setCursor(Qt.SizeVerCursor)
        self.bottomGrip.setCursor(Qt.SizeVerCursor)
        QSizeGrip(self.cornerGripLT)
        QSizeGrip(self.cornerGripLB)
        QSizeGrip(self.cornerGripRT)
        QSizeGrip(self.cornerGripRB)

        self.ScreenShotBtn.clicked.connect(self.screenshot)

        self.show()
        self.textScreen.show()

        self.adjustGripSize(10)
        # print(self.rect())
        self.resizeFunc = None
        self.getCornerCoor()
        # print(self.geometry().bottom())

    def getCornerCoor(self):
        # get widget coor
        self.cornerw = self.cornerGripLT.width()
        pass

    def adjustGripSize(self, size):
        self.cornerGripLT.setMinimumWidth(size)
        self.cornerGripLT.setMinimumHeight(size)
        self.cornerGripLB.setMinimumWidth(size)
        self.cornerGripLB.setMinimumHeight(size)
        self.cornerGripRT.setMinimumWidth(size)
        self.cornerGripRT.setMinimumHeight(size)
        self.cornerGripRB.setMinimumWidth(size)
        self.cornerGripRB.setMinimumHeight(size)
        self.bottomGrip.setMinimumHeight(size)
        self.topGrip.setMinimumHeight(size)
        self.rightGrip.setMinimumWidth(size)
        self.leftGrip.setMinimumWidth(size)
        pass

    # Properti unuk mouse event dari QtWidget/QtMainWindow/QtFrame
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos() #get current mouse position on global desktop area
        self.mousePos = event.pos() #get current mouse position on application area
        self.resizeFunc = None

        #these if statement check if the pressed mouse in the specific location (central area or left/right/top/bottom edge), also responsive with the window size that will be changed
        if (event.pos() in self.rect().adjusted(self.cornerw,self.cornerw,-self.cornerw,-self.cornerw)):
            self.resizeFunc = self.moveWin

        if (event.pos() in self.leftGrip.rect().adjusted(0, self.cornerw, 0, 0)):
            self.resizeFunc = self.resizeLeft

        if (event.pos() in self.rightGrip.rect().adjusted(self.rect().width() - self.cornerw, self.cornerw, self.rect().width() - self.cornerw, 0)):
            self.resizeFunc = self.resizeRight
        if (event.pos() in self.topGrip.rect().adjusted(self.cornerw,0,self.cornerw,0)):
            self.resizeFunc = self.resizeTop

        if (event.pos() in self.bottomGrip.rect().adjusted(self.cornerw,self.rect().height()-self.cornerw,self.cornerw,self.rect().height()-self.cornerw)):
            self.resizeFunc = self.resizeBottom  

        
        
    
    def mouseMoveEvent(self, event):
        # ev.pos => (x, y) (start with 0,0 on top left window)
        # ev.globalPos => (x, y) (start with 0,0 on top left desktop)
        if(self.resizeFunc == self.moveWin):
            delta = event.globalPos() - self.oldPos
            # print(delta)
            self.resizeFunc(delta)
            self.oldPos = event.globalPos()
        if((self.resizeFunc == self.resizeTop) or (self.resizeFunc == self.resizeLeft)):
            # print('masuk')
            delta = event.pos() - self.mousePos
            self.resizeFunc(delta)
        if((self.resizeFunc == self.resizeBottom) or (self.resizeFunc == self.resizeRight)):
            # print('masuk2')
            delta = event.pos() - self.mousePos
            self.resizeFunc(delta)
            self.mousePos = event.pos()
    
    def mouseReleaseEvent(self, event):
        self.mousePos = None
        self.globalPos = None
        self.resizeFunc = None

    def moveWin(self, delta):
        self.move(self.x() + delta.x(), self.y() + delta.y())

    def resizeLeft(self, delta):
        width = max(self.minimumWidth(), self.width() - delta.x())
        geo = self.geometry()
        geo.setLeft(geo.right() - width)
        self.setGeometry(geo)

    def resizeTop(self, delta):
        # window = self.window()
        height = max(self.minimumHeight(), self.height() - delta.y())
        geo = self.geometry()
        geo.setTop(geo.bottom() - height)
        self.setGeometry(geo)

    def resizeRight(self, delta):
        # window = self.window()
        width = max(self.minimumWidth(), self.width() + delta.x())
        self.resize(width, self.height())

    def resizeBottom(self, delta):
        # window = self.window()
        height = max(self.minimumHeight(), self.height() + delta.y())
        self.resize(self.width(), height)

    def screenshot(self):
        if not self.takingss:
            self.takingss = True
            # Set window Opacity to 0 to get clean screenshot
            self.setWindowOpacity(0)

            # Get the geometry (position and size) of your window
            window_geometry = self.geometry()
            x, y, width, height = window_geometry.x(), window_geometry.y(), window_geometry.width(), window_geometry.height()

            # Delay (just in case)
            time.sleep(0.3)

            # Capture gambar menggunakan pyautogui
            screenshot = pyautogui.screenshot(region=(x, y, width, height))

            # Save gambar menjadi file
            screenshot.save("screenshot.png")

            # Mengembalikan opacity semula
            # self.setWindowOpacity(self.setWinOpacity)
            self.setWindowOpacity(self.setWinOpacity)

            # Delay (just in case)
            time.sleep(0.6)

            self.textScreen.txtProcessing()

            self.takingss = False
    
    def closeScreen(self):
        self.textScreen.clearTxt()
        self.close()
        self.textScreen.close()    
    
   
if (__name__ == "__main__"):
    app = QApplication(sys.argv)
    screen = ScreenShot()
    app.exec_()