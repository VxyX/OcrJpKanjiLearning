from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QUrl
from PyQt5 import uic
from pprint import pprint

from parsing import Parse
from ocr import Capture
from translate import translate_text

class TextScreen(QMainWindow):
    def __init__(self):
        super(TextScreen, self).__init__()

        # load .ui file
        uic.loadUi("src/gui/textScreen.ui", self)

        viewJp = QWebEngineView(self)
        viewTl = QWebEngineView(self)
        self.verticalLayout.addWidget(viewJp)
        self.verticalLayout.addWidget(viewTl)
        viewJp.setUrl(QUrl.fromLocalFile('/src/teshtml.html'))
        viewTl.setUrl(QUrl.fromLocalFile('/src/teshtml2.html'))
        # self.parse = Parse()
        

    def labelklik(self):
        print('atas')

    def setText(self):
        capture = Capture()
        parse = Parse()
        jpText = capture.getText()
        jpText = jpText.replace('\n','')
        jpParseTxt = parse.jpParse1(jpText)

        pprint(jpParseTxt)

        tlTxt = translate_text(jpText, "en")
        # self.jpTxt.setHtml("<html><body><ruby>漢<rp>(</rp><rt>かん</rt><rp>)</rp>字<rp>(</rp><rt>じ</rt><rp>)</rp></ruby></body></html>")
        # self.tlTxt.setText(tlTxt)
        # self.tlText.setText(tlText)