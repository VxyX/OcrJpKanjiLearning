import typing
import pyautogui
import time
import threading
import multiprocessing
from PyQt5.QtWidgets import QMainWindow, QApplication, QSizeGrip
from PyQt5 import uic
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys

from txtscreen import TextScreen

from imgpreproc import ImProc

from ocr import Ocr

from pprint import pprint

class ScreenCapture(QMainWindow):
    def __init__(self, txtScreen : TextScreen):
        super(ScreenCapture, self).__init__()

        # load file
        self.uifile = "src/gui/screenCapture copy.ui"
        self.stylefile = "src/style/screenshot.qss"
        self.textScreen = txtScreen
        self.imgProcScreen = ImProc()
        self.imgProcScreenShow = False
        self.runningThread = None
        self.ocr = Ocr()
        self.jpTxt =''
        
        uic.loadUi(self.uifile, self)
        with open(self.stylefile,"r") as fh:
            self.setStyleSheet(fh.read())

        # set transparancy
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWinOpacity = 1
        self.setWindowOpacity(self.setWinOpacity)
        self.takingss = False

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
        self.PreProcessBtn.clicked.connect(self.tampilPreprocessImg)
        self.ssThread = None
        # show window
        self.show()

        # adjust element
        self.resize(600,200)
        self.adjustGripSize(15)
        self.resizeFunc = None
        self.getCornerCoor()

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
            self.resizeFunc(delta)
            self.oldPos = event.globalPos()

        if((self.resizeFunc == self.resizeTop) or (self.resizeFunc == self.resizeLeft)):
            delta = event.pos() - self.mousePos
            self.resizeFunc(delta)

        if((self.resizeFunc == self.resizeBottom) or (self.resizeFunc == self.resizeRight)):
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
        height = max(self.minimumHeight(), self.height() - delta.y())
        geo = self.geometry()
        geo.setTop(geo.bottom() - height)
        self.setGeometry(geo)

    def resizeRight(self, delta):
        width = max(self.minimumWidth(), self.width() + delta.x())
        self.resize(width, self.height())

    def resizeBottom(self, delta):
        height = max(self.minimumHeight(), self.height() + delta.y())
        self.resize(self.width(), height)

    def closeScreen(self):
        self.textScreen.fclose = True
        self.textScreen.clearTxt()
        self.imgProcScreen.closeScreen()
        self.close()
        self.textScreen.close()  
################## End of Custom Window Method ######################
    
    def screenshotThread(self):
        self.ssThread = ScreenshotThread(self.screenshot)
        self.ssThread.finished.connect(lambda: self.procImg)
        self.ssThread.start()
        

    def screenshot(self):
        # time.sleep(100)
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
            screenshot.save("imgpreproc.png")
            self.imgProcScreen.setImage("imgpreproc.png")
            

            # Mengembalikan opacity semula
            # self.setWindowOpacity(self.setWinOpacity)
            self.setWindowOpacity(self.setWinOpacity)

            # Delay (just in case)
            time.sleep(0.6)
            self.procImg()
            # self.runningThread1 = MultThread(self.textScreen.txtProcessing, 'screenshot.png')
            # self.runningThread2 = MultThread(self.textScreen.txtProcessing, 'processedimg.png')
            
                    # self.textScreen.txtProcessing('screenshot.png')
                
           
            
            self.takingss = False

    def procImg(self):
        if self.runningThread:
            if self.runningThread.isRunning():
                self.runningThread.stop()
        try:
            # print(self.imgProcScreen.isEnabled_())
            if self.imgProcScreen.isEnabled_():
                self.imgProcScreen.processImg('imgpreproc.png')
                self.runningThread = OcrThread(self.ocr, 'imgpreproc.png')
                self.runningThread.jpTxt.connect(self.ocrThreadSet)
                self.runningThread.finished.connect(lambda: self.ocrThreadFinished(self.jpTxt))
                self.runningThread.start()
                # self.textScreen.txtProcessing('processedimg.png')
                pass
            else:
                self.runningThread = OcrThread(self.ocr, 'screenshot.png')
                self.runningThread.jpTxt.connect(self.ocrThreadSet)
                self.runningThread.finished.connect(lambda: self.ocrThreadFinished(self.jpTxt))
                self.runningThread.start()
        except Exception as e:
            print(e)
        pass
      
    def tampilPreprocessImg(self) :
        if not self.imgProcScreen.isShown():
            self.imgProcScreen.show()
            self.imgProcScreenShow = True
        else:
            self.imgProcScreen.raise_()

        pass

    def ocrThreadSet(self, jpTxt):
        self.jpTxt = jpTxt

    def ocrThreadFinished(self, jpTxt):
        self.textScreen.txtProcessing(jpTxt)

class OcrThread(QThread):

    jpTxt = pyqtSignal(object)
    def __init__(self, func_to_run, img):
        super(OcrThread, self).__init__()
        self.func = func_to_run
        self.img = img

    def run(self):
        txt = self.func.getText(self.img)
        self.jpTxt.emit(txt)
        
        pass

    def stop(self):
        self.terminate()
        pass

class ScreenshotThread(QThread):

    jpTxt = pyqtSignal(object)
    def __init__(self, screenshot_func):
        super(ScreenshotThread, self).__init__()
        self.screenshot = screenshot_func

    def run(self):
        self.screenshot()
        
        pass

    def stop(self):
        self.terminate()
        pass
   
if (__name__ == "__main__"):
    app = QApplication(sys.argv)
    screen = ScreenCapture(TextScreen(None))
    app.exec_()