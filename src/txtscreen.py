from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QUrl
from PyQt5 import uic
from pprint import pprint
from bs4 import BeautifulSoup
import sys


from parsing import Parse
from ocr import Capture
from translate import translate_text

class TextScreen(QMainWindow):
    def __init__(self):
        super(TextScreen, self).__init__()

        self.jpHtml = 'src/html/jpText.html'
        self.tlHtml = 'src/html/tlText.html'

        # load file
        uic.loadUi("src/gui/textScreen.ui", self)
        with open(self.jpHtml, "r", encoding='utf-8') as file:
            self.jpTxt = BeautifulSoup(file, "html.parser")
        with open(self.tlHtml, "r", encoding='utf-8') as file:
            self.tlTxt = BeautifulSoup(file, "html.parser")

        self.jpBody = self.jpTxt.find('body')
        self.tlBody = self.tlTxt.find('body')

        viewJp = QWebEngineView(self)
        viewTl = QWebEngineView(self)
        self.verticalLayout.addWidget(viewJp)
        self.verticalLayout.addWidget(viewTl)
        viewJp.setUrl(QUrl.fromLocalFile('/src/teshtml.html'))
        viewTl.setUrl(QUrl.fromLocalFile('/src/teshtml2.html'))
        
        self.show()
        

    def labelklik(self):
        print('atas')

    def furigana(self, text, jenis_huruf='hiragana'or'katakana'or'romaji'):
        txt = text
        new_txt = ''
        if jenis_huruf == 'katakana':
            return txt
        
        for char in txt:
            katakana_code = ord(char)
            if jenis_huruf == 'hiragana':
                # Periksa apakah karakter adalah katakana
                if 0x30A1 <= katakana_code <= 0x30F6:
                    # Kode hiragana adalah kode katakana - 96
                    hiragana_code = katakana_code - 96 
                    hiragana_character = chr(hiragana_code)
                    new_txt += hiragana_character
                else:
                    # Jika bukan karakter katakana, tambahkan karakter aslinya
                    new_txt += char
            

        return new_txt
        pass

    def txtProcessing(self):
        capture = Capture('Screenshot_340.png')
        parse = Parse()
        
        jpParagraph = self.jpTxt.new_tag('p')
        tlParagraph = self.tlTxt.new_tag('p')
        kanji = ''
        first_part = ''
        second_part = ''

        jpText = capture.getText()
        jpText = jpText.replace('\n','')
        jpParseTxt = parse.jpParse1(jpText)

        for word in jpParseTxt:
            kanji = word[0]

            if word[1]:
                # split kanji and other text
                # fix problem like こんな風に where the kanji in between 2 hiragana
                split_index = kanji.find(word[1][0])
                if split_index != -1:
                    first_part = kanji[:split_index] 
                    second_part = kanji[split_index + len(word[1][0]):]
                
                ruby = self.jpTxt.new_tag("ruby")
                ruby.append(word[1][0])
                rt = self.jpTxt.new_tag("rt")
                rt.append(self.furigana(word[1][1], 'hiragana'))
                ruby.append(rt)

            if first_part or second_part:
                if first_part:
                    jpParagraph.append(first_part)
                if ruby:
                    jpParagraph.append(ruby)
                if second_part:
                    jpParagraph.append(second_part)
                first_part = ''
                second_part = ''
            else:
                jpParagraph.append(kanji)
        
        tlTxt = translate_text(jpText, "en")
        tlParagraph.append(tlTxt)
        self.setText(jpParagraph, tlParagraph)

    def setText(self, jpTxt, tlTxt):
        self.jpBody.string = ''
        self.tlBody.string = ''
        self.jpBody.append(jpTxt)
        self.tlBody.append(tlTxt) 
        self.saveTxt()

    def clearTxt(self):
        self.jpBody.string = ''
        self.tlBody.string = ''
        self.saveTxt()

    def saveTxt(self):
        with open(self.jpHtml, 'w', encoding='utf-8') as file:
            file.write(str(self.jpTxt))
        with open(self.tlHtml, 'w', encoding='utf-8') as file:
            file.write(str(self.tlTxt))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = TextScreen()
    app.exec_()