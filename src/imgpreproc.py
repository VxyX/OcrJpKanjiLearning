import sys
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImageReader, QImage, QShowEvent
from PyQt5.QtWidgets import  QApplication, QMainWindow, QLabel, QSlider, QVBoxLayout, QWidget, QPushButton, QFileDialog
import cv2
import os

class ImProc(QMainWindow):
    def __init__(self, **kwarg) -> None:
        super().__init__()
        # load file
        uic.loadUi("src/gui/preProcSettings.ui", self)

        # init
        self.thresholdSlider.setRange(0, 255)
        self.threshold_value = self.thresholdSlider.value()
        self.isShow = False
        self.isMenu = False
        # self.imgProcLabel.setScaledContents(True)
        self.file_path = 'preprocimg.png'
        img_path = kwarg.get("img_path")
        # print(img_path)
        if img_path is not None:
            self.file_path = img_path
        if os.path.exists(self.file_path):
            # print('ada')
            self.initImg = cv2.imread(self.file_path)
            self.lastProcImg = self.initImg
            self.procImg = self.initImg
            self.grayscaleImg = cv2.cvtColor(self.initImg, cv2.COLOR_BGR2GRAY)
            self.invertImg = cv2.bitwise_not(self.initImg)
            self.imgheight, self.imgwidth, channel = self.initImg.shape
            # print(type(self.imgwidth), self.imgheight, self.initImg.shape)

        self.preProcSwitch.stateChanged.connect(self.imProcToggle)
        self.thresholdSlider.valueChanged.connect(self.thresholdImgFunc)
        self.invertSwitch.stateChanged.connect(self.invertImgFunc)
        self.grayscaleSwitch.stateChanged.connect(self.grayscaleImgFunc)

        self.thresholdSlider.setEnabled(False)
        self.invertSwitch.setEnabled(False)
        self.grayscaleSwitch.setEnabled(False)


        # first image shown to UI 
        self.showImg(self.initImg)
        
    def isShown(self):
        return self.isShow

    def closeEvent(self, event):
        if self.isMenu:
            self.isShow = False
            event.accept()
        else:
            self.hide()
            self.isShow = False
            event.ignore()
        
    def closeScreen(self):
        self.isMenu = True
        self.close()

    def rescale_pixmap(self, scale_down=None, **kwargs):
        # Problems:
        # -Resize downscale not effective
        # - currently fix with adding margin -10 to pixmap
        if not self.imgpixmap:
            return
        
        pixmap = self.imgpixmap

        # if scale_down:
        #     selisih_w = kwargs.get("selisih_w")
        #     selisih_h = kwargs.get("selisih_h")
        #     new_width = pixmap.width() - selisih_w
        #     new_height = pixmap.height() - selisih_h
        #     pixmap = pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio)
        try:
            pixmap = pixmap.scaled(self.imgProcLabel.width() - 10, self.imgProcLabel.height() - 10, Qt.KeepAspectRatio)
        except Exception as e:
            print(e)

        self.imgProcLabel.setPixmap(pixmap)
        pass

    def resizeEvent(self, event):
        self.rescale_pixmap()
        
    def showEvent(self, event) -> None:
        self.rescale_pixmap()
        self.isShow = True
        pass

    def setImage(self, img_path):
        if os.path.exists(img_path):
            self.initImg = cv2.imread(img_path)
            self.lastProcImg = self.initImg
            self.procImg = self.initImg
            self.grayscaleImg = cv2.cvtColor(self.initImg, cv2.COLOR_BGR2GRAY)
            self.invertImg = cv2.bitwise_not(self.initImg)
            self.imgheight, self.imgwidth, channel = self.initImg.shape
        self.showImg(self.initImg)
        pass

    def processImg(self, img_path):
        if os.path.exists(img_path):
            self.initImg = cv2.imread(img_path)
            self.lastProcImg = self.initImg
            self.procImg = self.initImg
            self.grayscaleImg = cv2.cvtColor(self.initImg, cv2.COLOR_BGR2GRAY)
            self.invertImg = cv2.bitwise_not(self.initImg)
            self.imgheight, self.imgwidth, channel = self.initImg.shape

            img = self.initImg
            if self.invertSwitch.isChecked():
                inv_img = cv2.bitwise_not(img)
                img = inv_img
                pass
            if self.grayscaleSwitch.isChecked():
                gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                img = gray_img
                pass

            self.threshold_value = self.thresholdSlider.value()
            if self.threshold_value > 0:
                try:
                    _, thresholded_image = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), self.threshold_value, 255, cv2.THRESH_BINARY)
                except:
                    _, thresholded_image = cv2.threshold(img, self.threshold_value, 255, cv2.THRESH_BINARY)
                    pass
                img = thresholded_image
            
            if self.preProcSwitch.isChecked():
                self.showImg(img)
            cv2.imwrite("processedimg.png", img)

        else:
            return
        
        pass

    def isEnabled_(self) -> bool:
        return self.preProcSwitch.isChecked()

    def showImg(self, image):
        if not image.any():
            return
        
        self.procImg = image
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # self.imgheight, self.imgwidth, channel = image_rgb.shape
        bytes_per_line = 3 * self.imgwidth
        q_image = QImage(image_rgb.data, self.imgwidth, self.imgheight, bytes_per_line, QImage.Format_RGB888)
        
        
        self.imgpixmap = QPixmap.fromImage(q_image)
        # pixmap = pixmap.scaled(self.imgLabelWidth, self.imgLabelHeight, aspectRatioMode=1)
        pixmap = self.imgpixmap.scaled(self.imgProcLabel.width() - 10, self.imgProcLabel.height() - 10, Qt.KeepAspectRatio)
        
        self.imgProcLabel.setPixmap(pixmap)
        
        pass
    
    def imProcToggle(self, state):
        if state == 2:
            self.thresholdSlider.setEnabled(True)
            self.invertSwitch.setEnabled(True)
            self.grayscaleSwitch.setEnabled(True)
            pass
        else:
            
            self.thresholdSlider.setValue(0)
            self.invertSwitch.setChecked(False)
            self.grayscaleSwitch.setChecked(False)

            self.thresholdSlider.setEnabled(False)
            self.invertSwitch.setEnabled(False)
            self.grayscaleSwitch.setEnabled(False)

            if self.initImg.any():
                self.showImg(self.initImg)
                self.lastProcImg = self.initImg
            pass
        pass

    def invertImgFunc(self, state):
        self.procImg = cv2.bitwise_not(self.procImg)
        
        if state == 2:
            self.lastProcImg = self.invertImg
            pass
        else:
            if self.grayscaleSwitch.isChecked():
                self.lastProcImg = self.grayscaleImg
            else:
                self.lastProcImg = self.initImg
        self.showImg(self.procImg)
        pass
    
    def grayscaleImgFunc(self, state):
        if state == 2:
            try:
                self.procImg = cv2.cvtColor(self.procImg, cv2.COLOR_BGR2GRAY)
            except:
                pass
            self.lastProcImg = self.grayscaleImg
            pass
        else:
            if self.invertSwitch.isChecked():
                self.lastProcImg = self.invertImg
            else:
                self.lastProcImg = self.initImg
            self.procImg = self.lastProcImg
        self.showImg(self.procImg)
        pass

    def thresholdImgFunc(self):
        self.sliderValueLabel.setText(str(self.thresholdSlider.value()))
        init = self.lastProcImg
        img = self.grayscaleImg
        if self.invertSwitch.isChecked():
            img = cv2.bitwise_not(img)
        _, thresholded_image = cv2.threshold(img, self.thresholdSlider.value(), 255, cv2.THRESH_BINARY)
        # if self.grayscaleSwitch.isChecked():
        #     _, thresholded_image = cv2.threshold(img, self.thresholdSlider.value(), 255, cv2.THRESH_BINARY)
        # else:
        #     try:
        #         _, thresholded_image = cv2.threshold(img, self.thresholdSlider.value(), 255, cv2.THRESH_BINARY)
        #     except:
                # pass
        
        if self.thresholdSlider.value() == 0:
            if self.invertSwitch.isChecked():
                self.procImg = thresholded_image
            else:
                self.procImg = init
        else:
            self.procImg = thresholded_image
        self.threshold_value = self.thresholdSlider.value()
        self.showImg(self.procImg)

        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = ImProc(img_path='Screenshot_352.png')
    a.show()
    print(a.isEnabled_())
    
    app.exec_()