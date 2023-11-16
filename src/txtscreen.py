from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWidgets import QMainWindow, QApplication, QTextBrowser
from PyQt5.QtCore import QUrl, pyqtSlot, Qt, QEvent, QPoint, QRect
from PyQt5 import uic
from pprint import pprint
from bs4 import BeautifulSoup
import sys
from jisho import Dict

from parsing import Parse
from ocr import Capture
from translate import translate_text

class TextScreen(QMainWindow):
    def __init__(self):
        super(TextScreen, self).__init__()

        self.kamus = Dict()
        self.showKamus = False
        self.globTxtPos = None
        self.globTxtRect = None
        self.jpHtmlFile = 'src/html/jpText.html'
        # self.jpHtmlFile = 'tes.html'
        # self.tlHtmlFile = 'src/html/tlText.html'

        # load file
        uic.loadUi("src/gui/textScreen.ui", self)
        with open(self.jpHtmlFile, "r", encoding='utf-8') as file:
            self.jpTxt = BeautifulSoup(file, "html.parser")
        # with open(self.tlHtmlFile, "r", encoding='utf-8') as file:
        #     self.tlTxt = BeautifulSoup(file, "html.parser")

        self.jpBody = self.jpTxt.find('body')
        # self.tlBody = self.tlTxt.find('body')
        
        # set content
        self.viewJp = QWebEngineView(self)
        self.viewJp.setContextMenuPolicy(Qt.NoContextMenu)
        self.viewTl = QTextBrowser()
        # self.viewTl.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.viewTl.setStyleSheet("font-family: Arial; font-size: 16px; margin: 5px; font-weight:bold; border:none;")
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
        self.channel.registerObject('translate', self)
        self.viewJp.page().setWebChannel(self.channel)

        self.verticalLayout.addWidget(self.viewJp, stretch=2)
        self.verticalLayout.addWidget(self.viewTl, stretch=2)
  
        self.clearTxt()
        

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

    # txtProcessing -> need to optimize furigana function more if can...
    # Problems:
    # - romaji option for furigana
    # - furigana on specific kanji ex. -> 追<お> い 込<こ> み
    # - romaji on specific kanji like above
    # - romaji on the whole text ex. -> 追<o> い<i> 込<ko> み<mi>
    # currently:
    # - devide kanji that have 2 hiragana in between ex. -> こんな 風<ふう> に
    def txtProcessing(self):
        capture = Capture('screenshot.png')
        parse = Parse()
        
        jpDiv = self.jpTxt.new_tag('div')
        # tlDiv = self.tlTxt.new_tag('div')
        
        kata = ''
        first_part = ''
        second_part = ''
        kanji = ''
        kanji_list = []

        jpText = capture.getText()
        jpText = jpText.replace('\n','')
        jpText = jpText.replace(' ','')
        # jpText = jpText.replace(' ','')
        jpParseTxt = parse.jpParse1(jpText)

        pprint(jpParseTxt)
        print()

        for word in jpParseTxt:
            jpP = self.jpTxt.new_tag('p')
            jpP['class'] = 'jisho'
            w = self.jpTxt.new_tag("ruby")
            kata = word[0]
            con = False
            w['data-konjugasi'] = ''
            w['data-kelas'] = ''

            if(word[3]):
                for conj in word[3]:
                    if (w['data-konjugasi']):
                        w['data-konjugasi'] += ','+conj
                    else:
                        w['data-konjugasi'] += conj
            
            if(word[4]):
                for kelas in word[4]:
                    if (w['data-kelas']):
                        w['data-kelas'] += ','+kelas
                    else:
                        w['data-kelas'] += kelas
            
            # data access helper:
            # word[1][0] -> kanji
            # word[1][1] -> reading
            # kanji         - reading
            # word[1][0][0] - word[1][1][0]
            if word[1]: # check if kanji exist in the data
                temp_word = word[0]
                temp_kanji = word[1][0]
                temp_read = word[1][1]
                w_list = list(word[0])

                #iterate each letter for applying furigana better
                for letter in w_list:
                    
                    # this will skip if the current letter not matching the temp word letter
                    # this helps to fix problems if theres more than 1 letter/kanji inside temp word/kanji
                    # so it can skip the current leter
                    if temp_word:
                        if letter != temp_word[0]:
                            continue
                    else:
                        break
                    
                    # check if the letter is kanji
                    # if so, check if the kanji exist in word kanji data
                    # if exist, take the kanji data temporally
                    k_code = ord(letter)
                    if 0x4e00 < k_code <= 0x9fff:
                        # if the last letter is not a kanji,
                        # this will close the last rb tag
                        if con:
                            rt = self.jpTxt.new_tag("rt")
                            w.append(rt)
                            con = False
                        for string in temp_kanji:
                            if letter in string:
                                temp_w = string
                                break
                    # check if the temporal kanji data exist
                    # if so, process to make furigana
                    if temp_w:
                        k_index = temp_kanji.index(temp_w)
                        rb = self.jpTxt.new_tag("rb")
                        rb.append(temp_kanji[k_index])
                        rt = self.jpTxt.new_tag("rt")
                        rt.append(parse.furigana(temp_read[k_index], 'hiragana'))
                        w.append(rb)
                        w.append(rt)

                        # after furigana created, delete the current word on the list
                        # replacing temp_word is important
                        temp_kanji.remove(temp_kanji[k_index])
                        temp_read.remove(temp_read[k_index])
                        temp_word = temp_word.replace(temp_w,'',1)
                        # print(temp_word) 
                        temp_w = ''
                    else:
                        # print(letter)
                        w.append(letter)
                        con = True
                        temp_word = temp_word.replace(letter,'',1)

                # if the last letters iteration are not kanji,
                # this will close the rb tag with rt tag,
                if con:
                    rt = self.jpTxt.new_tag("rt")
                    w.append(rt)
                    con = False

                existing_classes = jpP.get('class')
                jpP['class'] = existing_classes + " furigana"
                jpP.append(w)
                # split kanji and other text
                # fix problem like こんな風に where the kanji in between 2 hiragana
                
                # split_index = kata.find(k[0])
                # if split_index != -1:
                #     first_part = kata[:split_index] 
                #     second_part = kata[split_index + len(k[0]):]
            
                # kanji = self.jpTxt.new_tag("ruby")
                # kanji.append(word[1][0])
                # rt = self.jpTxt.new_tag("rt")
                # rt.append(parse.furigana(word[1][1], 'hiragana'))
                # kanji.append(rt)

            # if first_part or second_part or kanji:
            #     if first_part:
            #         jpP.append(first_part)
            #     if kanji:
            #         jpP.append(kanji)
            #     if second_part:
            #         jpP.append(second_part)
            #     kanji = ''
            #     first_part = ''
            #     second_part = ''
            else:
                jpP.append(kata)

            jpDiv.append(jpP)
        # print(jpText)
        # return
        tlTxt = translate_text(jpText,'bing','en')
        # tlDiv.append(tlTxt)

        self.setText(jpDiv, tlTxt)
        # Menunggu seluruh text dan class load sepenuhnya
        self.viewJp.loadFinished.connect(self.addClickWord)

    @pyqtSlot()
    def getTranslate(self, txt):
        self.tltxt = txt


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

                    //p -> ruby
                    var ruby = element.querySelector('ruby')
                    var japaneseWord = element.textContent;
                    rect = element.getBoundingClientRect()
                    rects.push(rect)
                    if (ruby) {
                        //p -> ruby -> rb
                        var kanji = ruby.firstChild.textContent;
                        //p -> ruby -> rt
                        var reading = ruby.querySelector('rt').textContent;

                        pyweb.jishoReq(japaneseWord, rect.right, rect.bottom, rect.left, rect.top, kanji, reading);
                    } else {
                        pyweb.jishoReq(japaneseWord, rect.right, rect.bottom, rect.left, rect.top, '', '');
                    }
                    
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
        if (event.type() == QEvent.MouseButtonPress):
            if event.button() == Qt.LeftButton:
                self.oldPos = event.globalPos()

                if self.showKamus:
                    rect = self.kamus.geometry()
                    if (self.oldPos not in rect):
                        self.kamus.hide()
                        self.showKamus = False

                if self.globTxtRect:
                    if self.oldPos not in self.globTxtRect:
                        js = 'var ele = document.querySelector(".active"); ele.classList.remove("active");'
                        self.viewJp.page().runJavaScript(js)

        return super().eventFilter(source, event)

    # jika fungsi memiliki parameter, typedata harus ditentukan pada @pyqtSlot
    # jika ingin passing class objek, makah class harus menginherit QObject
    @pyqtSlot(str, int, int, int, int, str, str)
    def jishoReq(self, word, x, y, w, h, kanji, reading):
        # print(self.viewJp.mapToGlobal(QPoint(x,y)))
        # print(kanji, reading)
        self.globTxtPos = self.viewJp.mapToGlobal(QPoint(x,y))
        self.globTxtRect = QRect(self.globTxtPos.x(), self.globTxtPos.y(), x - w, y - h)

        # if (kanji and reading):
        #     self.kamus.search_jisho()

        self.kamus.moveWin(self.globTxtPos.x(), self.globTxtPos.y())
        self.kamus.show()
        self.showKamus = True

class CustomWebEnginePage(QWebEnginePage):
    # override print console js untuk debugging
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # Override the JavaScriptConsoleMessage method
        print(f"JavaScript Console Message: Level {level}, Message: {message}, Line Number: {lineNumber}, Source ID: {sourceID}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = TextScreen()
    screen.txtProcessing()
    screen.show()
    app.exec_()