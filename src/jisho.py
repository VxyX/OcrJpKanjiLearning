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
from parsing import Parse

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
        self.content.setPage(CustomWebEnginePage(self.content))
        self.content.setUrl(QUrl.fromLocalFile('/'+self.dictHtmlFile))

        self.winLayout.addWidget(self.content)
        # set transparancy
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen)

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
        self.movePanel(delta)
        self.oldPos = event.globalPos()

    def movePanel(self, delta):
        self.move(self.x() + delta.x(), self.y() + delta.y())

    def tampilKamus2(self, word, kanjis, kanji_readings, lemma, inflec, classif, kamus_dat):
        
        jisho_dat = kamus_dat
        if not jisho_dat:
            js = f"""
            document.getElementById("word").innerHTML = 'Kata tidak ditemukan';
            """
            self.content.page().runJavaScript(js)

        ############# Word Display ##################
        ruby = self.dictTxt.new_tag("ruby")
        lemma_kanj = []
        if (lemma[0] != lemma[1]): # check if kanji exist in the data
            parser = Parse()
            # print("ada")
            lemma_kanj = parser.furigana(lemma[0], lemma[1])
            # print(lemma_kanj)
            temp_word = lemma[0]
            temp_kanji = lemma_kanj[0]
            temp_read = lemma_kanj[1]
            con = False
            for char in lemma[0]:
                k_code = ord(char)
                temp_w = ''
                if 0x4e00 < k_code <= 0x9fff:
                    # if the last letter is not a kanji,
                    # this will close the last rb tag
                    if con:
                        rt = self.dictTxt.new_tag("rt")
                        ruby.append(rt)
                        con = False
                    for string in temp_kanji:
                        if char in string:
                            temp_w = string
                            break
                # check if the temporal kanji data exist
                # if so, process to make furigana
                if temp_w:
                    k_index = temp_kanji.index(temp_w)
                    rb = self.dictTxt.new_tag("rb")
                    rb['class'] = 'kanji'
                    rb.append(temp_kanji[k_index])
                    rt = self.dictTxt.new_tag("rt")
                    rt['class'] = 'reading'
                    rt.append(temp_read[k_index])
                    ruby.append(rb)
                    ruby.append(rt)

                    # after furigana created, delete the current word on the list
                    # replacing temp_word is important
                    temp_kanji.remove(temp_kanji[k_index])
                    temp_read.remove(temp_read[k_index])
                    temp_word = temp_word.replace(temp_w,'',1)
                    # print(temp_word) 
                    temp_w = ''
                else:
                    # print(letter)
                    ruby.append(char)
                    con = True
                    temp_word = temp_word.replace(char,'',1)
            if con:
                    rt = self.dictTxt.new_tag("rt")
                    ruby.append(rt)
                    con = False
        else:
            ruby.append(lemma[0])      
        kata = str(ruby)
        ############# Word Display ##################
        ############# Senses Display ##################
        tag1_dict = []
        tag2_dict = []
        div_list = []
        for sense in jisho_dat[3]:
            div_sense = self.dictTxt.new_tag("div")
            div_sense['id'] = 'sense' #grouping tags and meanings

            div_tags = self.dictTxt.new_tag("div")
            div_tags['id'] = 'tags'

            div_meanings = self.dictTxt.new_tag("div")
            div_meanings['id'] = 'meanings'

            div_tag1 = self.dictTxt.new_tag("div")
            div_tag1['class'] = 'group_tag1'
            if sense[0]:
                for tag1 in sense[0]:
                    p = self.dictTxt.new_tag("p")
                    p['class'] = 'tag1'
                    p.append(tag1)
                    div_tag1.append(p)
                    pass
            
            div_tag2 = self.dictTxt.new_tag("div")
            div_tag2['class'] = 'group_tag2'
            if sense[1]:
                for tag2 in sense[1]:
                    p = self.dictTxt.new_tag("p")
                    p['class'] = 'tag2'
                    p.append(tag2)
                    div_tag2.append(p)

            ul = self.dictTxt.new_tag("ul")
            if sense[2]:
                for meaning in sense[2]:
                    li = self.dictTxt.new_tag("li")
                    li.append(meaning)
                    ul.append(li)

            div_tags.append(div_tag1)
            div_tags.append(div_tag2)
            div_meanings.append(ul)

            div_sense.append(div_tags)
            div_sense.append(div_meanings)

            div_list.append(str(div_sense))
            
        senses = ''.join(div_list)
        senses = senses.replace('\'','\\\'')
        # print(senses)
        ############# Senses Display ##################
        js = f"""
        document.getElementById("word").innerHTML = '{kata}';
        document.getElementById("senses").innerHTML = '{senses}';
        """
        self.content.page().runJavaScript(js)
        pass

    def tampilKamus(self, word, kanji, kanji_reading, lemma, inflec, classif):
        # Data
        # [0] -> Kanji
        # [1] -> Reading
        # [2] -> JLPT Level
        # [3][0] -> Part of Speech
        # [3][1] -> Meanings (list)
        inflection = False
        inflection_list = []
        if (not (word == lemma[0] or word == lemma[1])):
            inflection = True

        
        data = self.cariKata(word, part_of_speech=classif)

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
    def cariKata(self, word, reading=None, part_of_speech=None):

        url = f"https://jisho.org/api/v1/search/words?keyword={word}"
        if reading:
            url += f"%20{reading}"
        if part_of_speech:
            url += f"%20%23{part_of_speech}"

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
            # pprint(data["data"][0])
            if data["meta"]["status"] == 200 and data["data"]:
                # Ambil data pertama (paling relevan)
                result = data["data"][0]
                try:
                    kanji = result["japanese"][0]["word"]
                except:
                    kanji = ''
                    pass
                hiragana = result["japanese"][0]["reading"]
                jlpt = result["jlpt"]
                senses = []
                # limit definition more than X
                limit_definition = 5
                count_sense = 0
                for sense in result["senses"]:
                    if count_sense == limit_definition:
                        break
                    more_info = sense["tags"]
                    kelas = sense["parts_of_speech"]
                    # testing for kamus tl indo
                    # for tl in kelas:
                    #     kelas_tl = translate.translate_text(tl,'bing','id','en')
                    meanings = sense["english_definitions"]
                    # for tl in meanings:
                    #     meanings_tl = translate.translate_text(tl,'bing','id','en')
                    senses.append([more_info, kelas, meanings])
                    count_sense += 1
                # kelas = [",".join(sense["parts_of_speech"]) for sense in result["senses"]]
                # meanings = [", ".join(sense["english_definitions"]) for sense in result["senses"]]
                return [kanji, hiragana, jlpt, senses]
            else:
                return False
        else:
            return False
        
    def movePanel(self, x, y):
        self.move(x, y)

class CustomWebEnginePage(QWebEnginePage):
    # override print console js untuk debugging
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # Override the JavaScriptConsoleMessage method
        print(f"JavaScript Console Message: Level {level}, Message: {message}, Line Number: {lineNumber}, Source ID: {sourceID}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Dict()
    search_word = '甘えすぎ'
    meanings = widget.cariKata(search_word)
    pprint(meanings)
    # print(f"Makna kata {japanese_word}: {', '.join(meanings)}")
    widget.show()
    sys.exit(app.exec_())