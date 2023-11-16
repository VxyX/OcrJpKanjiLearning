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
import translate

# cwd = os.getcwd()  # Get the current working directory (cwd)
# files = os.listdir(cwd)  # Get all the files in that directory
# print("Files in %r: %s" % (cwd, files))

class Dict(QWidget):
    def __init__(self, x=100, y=100):
        super(Dict, self).__init__()

        self.kanjivg = None
        self.word = None
        self.meanings = None
        self.part_of_speech = None
        self.jlpt_lv = None

        # load file
        self.dictHtmlFile = 'src/html/dictScreen.html'
        with open(self.dictHtmlFile, "r", encoding='utf-8') as file:
            self.dictTxt = BeautifulSoup(file, "html.parser")

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
        self.content.setUrl(QUrl.fromLocalFile('/'+self.dictHtmlFile))

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

    def addWord(self, word, kanji="", kanji_reading=""):
        # Data
        # [0] -> Kanji
        # [1] -> Reading
        # [2] -> JLPT Level
        # [3][0] -> Part of Speech
        # [3][1] -> Meanings (list)
        data = self.search_jisho(word)

        container = self.dictTxt.new_tag("div")
        header_cont = self.dictTxt.new_tag("div") # word
        info_cont = self.dictTxt.new_tag("div") # reading, jlpt, part o spch
        meanings_cont = self.dictTxt.new_tag("div") # meanings
        kvg_cont = self.dictTxt.new_tag("div") # writing animation

        # Header Section
        titleP = self.dictTxt.new_tag("p")
        titleP['class'] = 'title'
        if (kanji and kanji_reading):
            kan = ''
            first_part = ''
            second_part = ''
            kan = self.dictTxt.new_tag("ruby")
            kan.append(kanji)
            furi = self.dictTxt.new_tag("rt")
            furi.append(kanji_reading)
            kan.append(furi)
            
            split_index = word.find(kanji)
            if split_index != -1:
                first_part = word[:split_index] 
                second_part = word[split_index + len(kanji):]
            if first_part:
                titleP.append(first_part)
            if kanji:
                titleP.append(kan)
            if second_part:
                titleP.append(second_part)
        else :
            titleP.append(word)
        header_cont.append(titleP)

        # Word Info Section
        readP = self.dictTxt.new_tag("p")
        readP.append(data[1])
        jlptP = self.dictTxt.new_tag("p")
        jlptP.append(data[2])
        p_of_sP = self.dictTxt.new_tag("p")
        p_of_sP.append(data[3])

        container.append(header_cont)
        # container.append(header_cont)
        # container.append(header_cont)
        # container.append(header_cont)



        pass

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
                kanji = result["japanese"][0]["word"]
                hiragana = result["japanese"][0]["reading"]
                jlpt = result["jlpt"]
                senses = []
                for sense in result["senses"]:
                    kelas = sense["parts_of_speech"]
                    # testing for kamus tl indo
                    # for tl in kelas:
                    #     kelas_tl = translate.translate_text(tl,'bing','id','en')
                    meanings = sense["english_definitions"]
                    # for tl in meanings:
                    #     meanings_tl = translate.translate_text(tl,'bing','id','en')
                    senses.append([kelas, meanings])
                # kelas = [",".join(sense["parts_of_speech"]) for sense in result["senses"]]
                # meanings = [", ".join(sense["english_definitions"]) for sense in result["senses"]]
                return [kanji, hiragana, jlpt, senses]
            else:
                return "Kata tidak ditemukan di Jisho.", None
        else:
            return "Terjadi kesalahan dalam mengakses API Jisho.", None
        
    def moveWin(self, x, y):
        self.move(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Dict()
    search_word = '買いませんでした'
    meanings = widget.search_jisho(search_word)
    pprint(meanings)
    # print(f"Makna kata {japanese_word}: {', '.join(meanings)}")
    # widget.show()
    sys.exit(app.exec_())