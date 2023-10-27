from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout
from PyQt5 import uic
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import Qt, QUrl
from bs4 import BeautifulSoup
from pprint import pprint #debugging
import sys
import requests
import xml.etree.ElementTree as ET
import os
import svgwrite
import tkinter as tk
from PIL import Image, ImageTk
import io
from svg.path import parse_path
from pprint import pprint

# cwd = os.getcwd()  # Get the current working directory (cwd)
# files = os.listdir(cwd)  # Get all the files in that directory
# print("Files in %r: %s" % (cwd, files))

class Kamus(QWidget):
    def __init__(self, x=100, y=100):
        super(Kamus, self).__init__()

        # load file
        self.kamusHtmlFile = 'src/html/kamus.html'
        with open(self.kamusHtmlFile, "r", encoding='utf-8') as file:
            self.jpTxt = BeautifulSoup(file, "html.parser")

        # create widget
        self.setWindowTitle('Frameless Widget Example')
        self.setGeometry(x, y, 250, 350)
        # self.setWindowFlag(Qt.WindowStaysOnTopHint)

        #create layout
        self.winLayout = QVBoxLayout()
        self.winLayout.setContentsMargins(0,0,0,0)
        self.contentVLayout = QVBoxLayout()

        # create webview
        self.content = QWebEngineView(self)
        self.content.setUrl(QUrl.fromLocalFile('/'+self.kamusHtmlFile))

        self.winLayout.addWidget(self.content)
        # set transparancy
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        

        self.setLayout(self.winLayout)
        # self.show()
        pass

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        # ev.pos => (x, y) (start with 0,0 on top left window)
        # ev.globalPos => (x, y) (start with 0,0 on top left desktop)
        delta = event.globalPos() - self.oldPos
        # print(delta)
        self.moveWin(delta)
        self.oldPos = event.globalPos()

    def moveWin(self, delta):
        self.move(self.x() + delta.x(), self.y() + delta.y())

    # Fungsi untuk mencari makna kata di Jisho menggunakan Jisho API
    def search_jisho(self, word):
        url = f"https://jisho.org/api/v1/search/words?keyword={word}"
        response = requests.get(url)
        # http://jisho.org/api/v1/search/words?keyword=%23jlpt-n5
        # What i need...
        # japanese word kanji (data->[0-?]->[japanese]->[0]->[word])
        # japanese word reading hiragana (data->[0-?]->[japanese]->[0]->[reading])
        # jlpt level (data->[0-?]->[jlpt]->[])
        # word type/part of speech/kelas kata (data->sense->[0-?]->part_of_speech->[])
        # meanings (data->sense->[0-?]->english_definitions->[])

        if response.status_code == 200:
            data = response.json()
            pprint(data["data"][0])
            if data["meta"]["status"] == 200 and data["data"]:
                # Ambil data pertama (paling relevan)
                result = data["data"][0]
                japanese_word = result["japanese"][0]["word"]
                meanings = [", ".join(sense["english_definitions"]) for sense in result["senses"]]
                return japanese_word, meanings
            else:
                return "Kata tidak ditemukan di Jisho.", None
        else:
            return "Terjadi kesalahan dalam mengakses API Jisho.", None
        
    def moveWin(self, x, y):
        self.move(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Kamus()
    search_word = '華麗'
    japanese_word, meanings = widget.search_jisho(search_word)
    print(meanings)
    print(f"Makna kata {japanese_word}: {', '.join(meanings)}")
    widget.show()
    sys.exit(app.exec_())