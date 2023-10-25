from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QUrl, pyqtSlot, QObject
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

        # page = CustomWebEnginePage()
        self.viewJp = QWebEngineView(self)
        self.viewTl = QWebEngineView(self)
        self.viewJp.setPage(CustomWebEnginePage(self.viewJp))

        # Objek pyweb dalam WebView harus dibuat sebelum run js
        self.channel = QWebChannel()
        self.channel.registerObject('pyweb', self)
        self.viewJp.page().setWebChannel(self.channel)

        self.verticalLayout.addWidget(self.viewJp)
        self.verticalLayout.addWidget(self.viewTl)
        self.viewJp.setUrl(QUrl.fromLocalFile('/'+self.jpHtml))
        self.viewTl.setUrl(QUrl.fromLocalFile('/'+self.tlHtml))

        self.clearTxt()
        
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
        capture = Capture('screenshot.png')
        parse = Parse()
        
        jpDiv = self.jpTxt.new_tag('div')
        tlDiv = self.tlTxt.new_tag('div')
        
        kata = ''
        first_part = ''
        second_part = ''
        kanji = ''

        jpText = capture.getText()
        jpText = jpText.replace('\n','')
        jpParseTxt = parse.jpParse1(jpText)

        # pprint(jpParseTxt)
        print()

        for word in jpParseTxt:
            jpP = self.jpTxt.new_tag('p')
            jpP['class'] = 'jisho'
            kata = word[0]

            if word[1]:
                # split kanji and other text
                # fix problem like こんな風に where the kanji in between 2 hiragana
                split_index = kata.find(word[1][0])
                if split_index != -1:
                    first_part = kata[:split_index] 
                    second_part = kata[split_index + len(word[1][0]):]
                
                kanji = self.jpTxt.new_tag("ruby")
                kanji.append(word[1][0])
                rt = self.jpTxt.new_tag("rt")
                rt.append(self.furigana(word[1][1], 'hiragana'))
                kanji.append(rt)

            if first_part or second_part or kanji:
                if first_part:
                    jpP.append(first_part)
                if kanji:
                    jpP.append(kanji)
                if second_part:
                    jpP.append(second_part)
                kanji = ''
                first_part = ''
                second_part = ''
            else:
                jpP.append(kata)

            jpDiv.append(jpP)
        
        tlTxt = translate_text(jpText, "en")
        tlDiv.append(tlTxt)

        self.setText(jpDiv, tlDiv)
        # Menunggu seluruh text dan class load sepenuhnya
        self.viewJp.loadFinished.connect(self.addClickWord)

    def addClickWord(self, ok):
        if ok:
            js = """
            // objek harus diinisialisasi untuk menghubungkan fungsi py ke js
            var pyweb;
            new QWebChannel(qt.webChannelTransport, function (channel) {
                pyweb = channel.objects.pyweb;
            });

            // membuat seluruh kata clickable
            var elements = document.querySelectorAll('.jisho');
            elements.forEach(function(element) {
                element.addEventListener('click', function() {
                    var japaneseWord = element.textContent;
                    pyweb.jishoReq(japaneseWord);
                });
            });
            """
            self.viewJp.page().runJavaScript(js)

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

        self.viewJp.setUrl(QUrl.fromLocalFile('/'+self.jpHtml))
        self.viewTl.setUrl(QUrl.fromLocalFile('/'+self.tlHtml))

    # jika fungsi memiliki parameter, typedata harus ditentukan pada @pyqtSlot
    # jika ingin passing class objek, makah class harus menginherit QObject
    @pyqtSlot(str)
    def jishoReq(self, kata):
        print(kata)

class CustomWebEnginePage(QWebEnginePage):

    # override print console js untuk debugging
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # Override the JavaScriptConsoleMessage method
        print(f"JavaScript Console Message: Level {level}, Message: {message}, Line Number: {lineNumber}, Source ID: {sourceID}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = TextScreen()
    screen.txtProcessing()
    app.exec_()