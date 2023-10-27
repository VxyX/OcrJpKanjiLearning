from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel
from PyQt5.QtCore import QUrl, pyqtSlot, QObject, Qt, QEvent, QPoint, QRect
from PyQt5 import QtGui, uic
from pprint import pprint
from bs4 import BeautifulSoup
import sys
from jisho import Kamus


from parsing import Parse
from ocr import Capture
from translate import translate_text

class TextScreen(QMainWindow):
    def __init__(self):
        super(TextScreen, self).__init__()

        self.kamus = Kamus()
        self.showKamus = False
        self.globTxtPos = None
        # self.globTxtRect = None
        self.jpHtmlFile = 'src/html/jpText.html'
        # self.tlHtmlFile = 'src/html/tlText.html'

        # load file
        uic.loadUi("src/gui/textScreen.ui", self)
        with open(self.jpHtmlFile, "r", encoding='utf-8') as file:
            self.jpTxt = BeautifulSoup(file, "html.parser")
        # with open(self.tlHtmlFile, "r", encoding='utf-8') as file:
        #     self.tlTxt = BeautifulSoup(file, "html.parser")

        self.jpBody = self.jpTxt.find('body')
        # self.tlBody = self.tlTxt.find('body')
        
        # page = CustomWebEnginePage()
        self.viewJp = QWebEngineView(self)
        self.viewJp.setContextMenuPolicy(Qt.NoContextMenu)
        self.viewTl = QLabel()
        self.viewTl.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.viewTl.setStyleSheet("font-family: Arial; font-size: 16px; margin: 5px; font-weight:bold")
        # self.viewTl = QWebEngineView(self)
        # self.viewTl.setContextMenuPolicy(Qt.NoContextMenu)
        self.viewJp.setPage(CustomWebEnginePage(self.viewJp))
        self.viewJp.setUrl(QUrl.fromLocalFile('/'+self.jpHtmlFile))
        # self.viewTl.setUrl(QUrl.fromLocalFile('/'+self.tlHtmlFile))
        # QWebEngine can't recieve event handler..
        # Thus should install the event handler manually
        self.viewJp.focusProxy().installEventFilter(self)
        # Objek pyweb dalam WebView harus dibuat sebelum run js
        self.channel = QWebChannel()
        self.channel.registerObject('pyweb', self)
        self.viewJp.page().setWebChannel(self.channel)

        self.verticalLayout.addWidget(self.viewJp)
        self.verticalLayout.addWidget(self.viewTl)
        
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
        # tlDiv = self.tlTxt.new_tag('div')
        
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
        # tlDiv.append(tlTxt)

        self.setText(jpDiv, tlTxt)
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
            var ele = document.querySelector('p');
            var rects = [];
            elements.forEach(function(element) {
                element.addEventListener('click', function() {
                    elements.forEach(function(p) {
                        p.classList.remove("active");
                    });
                    element.classList.add("active");
                    var japaneseWord = element.textContent;
                    rect = element.getBoundingClientRect()
                    rects.push(rect)
                    pyweb.jishoReq(japaneseWord, rect.right, rect.bottom, rect.left, rect.top);
                });
            });
            """
            self.viewJp.page().runJavaScript(js)

    def setText(self, jpTxt, tlTxt):
        self.jpBody.string = ''
        # self.tlBody.string = ''
        self.jpBody.append(jpTxt)
        # self.tlBody.append(tlTxt)
        self.viewJp.loadFinished.connect(lambda ok: self.viewTl.setText(tlTxt) if ok else None)
 
        self.saveTxt()

    def clearTxt(self):
        self.jpBody.string = ''
        # self.tlBody.string = ''
        self.saveTxt()

    def saveTxt(self):
        with open(self.jpHtmlFile, 'w', encoding='utf-8') as file:
            file.write(str(self.jpTxt))
        # with open(self.tlHtmlFile, 'w', encoding='utf-8') as file:
        #     file.write(str(self.tlTxt))

        self.viewJp.setUrl(QUrl.fromLocalFile('/'+self.jpHtmlFile))
        # self.viewTl.setUrl(QUrl.fromLocalFile('/'+self.tlHtmlFile))

    def eventFilter(self, source, event):
        # if (event.type() == QEvent.ChildAdded and
        #     source is self.viewJp and
        #     event.child().isWidgetType()):
        #     self._glwidget = event.child()
        #     self._glwidget.installEventFilter(self)
        # elif (event.type() == QEvent.MouseButtonPress and
        #       source is self._glwidget):
        #     print('web-view mouse-press:', event.pos())
        if (event.type() == QEvent.MouseButtonPress):
            if event.button() == Qt.LeftButton:
                # print(event.pos())
                self.oldPos = event.globalPos()
                if self.showKamus:
                    rect = self.kamus.geometry()
                    if (self.oldPos not in rect):
                        self.kamus.hide()
                        self.showKamus = False
                if self.globTxtPos:
                    if self.oldPos not in self.globTxtRect:
                        js = 'var ele = document.querySelector(".active"); ele.classList.remove("active");'
                        self.viewJp.page().runJavaScript(js)
            # print(event.pos())
        # print(source, event.type())
        return super().eventFilter(source, event)
        # print('tes')

    # def mouseReleaseEvent(self, event):
    #     self.oldPos = None

    # jika fungsi memiliki parameter, typedata harus ditentukan pada @pyqtSlot
    # jika ingin passing class objek, makah class harus menginherit QObject
    @pyqtSlot(str, int, int, int, int)
    def jishoReq(self, kata, x, y, w, h):
        # print(self.viewJp.mapToGlobal(QPoint(x,y)))
        self.globTxtPos = self.viewJp.mapToGlobal(QPoint(x,y))
        self.globTxtRect = QRect(self.globTxtPos.x(), self.globTxtPos.y(), x - w, y - h)
        print(self.globTxtRect)
        self.kamus.moveWin(self.globTxtPos.x(), self.globTxtPos.y())
        # self.kamus.moveWin(self.oldPos.x(), self.oldPos.y())
        self.kamus.show()
        self.showKamus = True
        pass

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