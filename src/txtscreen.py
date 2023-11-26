import typing
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWidgets import QMainWindow, QApplication, QTextBrowser
from PyQt5.QtCore import QObject, QUrl, pyqtSlot, Qt, QEvent, QPoint, QRect, QThread, pyqtSignal
from PyQt5 import uic
from pprint import pprint
from bs4 import BeautifulSoup
import sys
import time
import re

from jisho import Dict
from parsing import Parse
from ocr import Capture


class TextScreen(QMainWindow):
    def __init__(self):
        super(TextScreen, self).__init__()

        import translate
        self.tl = translate.Translate()
        self.kamus = Dict()
        self.showKamus = False
        self.globTxtPos = None
        self.globTxtRect = None
        self.jpHtmlFile = 'src/html/jpText.html'
        self.dataKamus = {}
        self.threads = {}
        # self.jpHtmlFile = 'tes.html'
        # self.tlHtmlFile = 'src/html/tlText.html'

        # app.focusChanged.connect(self.on_focusChanged)

        # load file
        uic.loadUi("src/gui/textScreen.ui", self)
        with open(self.jpHtmlFile, "r", encoding='utf-8') as file:
            self.jpHtml = BeautifulSoup(file, "html.parser")
        # with open(self.tlHtmlFile, "r", encoding='utf-8') as file:
        #     self.tlTxt = BeautifulSoup(file, "html.parser")

        self.jpBody = self.jpHtml.find('body')
        # self.tlBody = self.tlTxt.find('body')
        
        # set content
        self.jpTxt = QWebEngineView(self)
        self.jpTxt.setContextMenuPolicy(Qt.NoContextMenu)
        self.tlTxt = QTextBrowser()
        # self.viewTl.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tlTxt.setStyleSheet("font-family: Arial; font-size: 16px; margin: 5px; font-weight:bold; border:none;")
        # self.viewTl = QWebEngineView(self)
        # self.viewTl.setContextMenuPolicy(Qt.NoContextMenu)
        self.jpTxt.setPage(CustomWebEnginePage(self.jpTxt))
        self.jpTxt.setUrl(QUrl.fromLocalFile('/'+self.jpHtmlFile))
        # self.viewTl.setUrl(QUrl.fromLocalFile('/'+self.tlHtmlFile))
        # QWebEngine can't recieve event handler..
        # Thus should install the event handler manually
        self.jpTxt.focusProxy().installEventFilter(self)
        self.tlTxt.viewport().installEventFilter(self)
        # Objek pyweb dalam WebView harus dibuat sebelum run js
        self.channel = QWebChannel()
        self.channel.registerObject('pyweb', self)
        self.channel.registerObject('translate', self)
        self.jpTxt.page().setWebChannel(self.channel)

        self.verticalLayout.addWidget(self.jpTxt, stretch=2)
        self.verticalLayout.addWidget(self.tlTxt, stretch=2)
  
        self.clearTxt()
        
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
                        self.jpTxt.page().runJavaScript(js)
                        self.globTxtRect = None

        return super().eventFilter(source, event)
    
    # txtProcessing -> need to optimize furigana function more if can...
    # Problems:
    # - romaji option for furigana
    # - furigana on specific kanji ex. -> 追<お> い 込<こ> み
    # - romaji on specific kanji like above
    # - romaji on the whole text ex. -> 追<o> い<i> 込<ko> み<mi>
    # currently:
    # - devide kanji that have 2 hiragana in between ex. -> こんな 風<ふう> に


    def setText(self, jpTxt, tlTxt):
        self.jpBody.string = ''
        # self.tlBody.string = ''
        self.jpBody.append(jpTxt)
        # self.tlBody.append(tlTxt)
        self.jpTxt.loadFinished.connect(lambda ok: self.tlTxt.setText(tlTxt) if ok else None)
 
        self.saveTxt()

    # public method -> screen.py
    def clearTxt(self):
        self.jpBody.string = ''
        self.tlTxt.setText('')
        self.saveTxt()

    #private method
    def saveTxt(self):
        with open(self.jpHtmlFile, 'w', encoding='utf-8') as file:
            file.write(str(self.jpHtml))
        # with open(self.tlHtmlFile, 'w', encoding='utf-8') as file:
        #     file.write(str(self.tlTxt))

        self.jpTxt.setUrl(QUrl.fromLocalFile('/'+self.jpHtmlFile))
        # self.viewTl.setUrl(QUrl.fromLocalFile('/'+self.tlHtmlFile))
 
    @pyqtSlot()
    def getTranslate(self, txt):
        self.tltxt = txt

    # later note :
    # cut process if previous text is the same with current text
    def txtProcessing(self): #public method
        capture = Capture('screenshot.png')
        parse = Parse()
        
        jpDiv = self.jpHtml.new_tag('div')
        # tlDiv = self.tlTxt.new_tag('div')
        
        kata = ''
        first_part = ''
        second_part = ''
        kanji = ''
        kanji_list = []
        
        jpText = capture.getText()
        jpText = jpText.replace('\n',' ')
        print(jpText)
        pattern = "[\u4e00-\ufaff]\s|[\u4e00-\ufaff]\s+|[\u4e00-\ufaff]\t"
        pattern += "|[\u3040-\u309F]\s|[\u3040-\u309F]\s+|[\u3040-\u309F]\t" #hiragana
        pattern += "|[\u30A0-\u30ff]\s|[\u30A0-\u30ff]\s+|[\u30A0-\u30ff]\t"
        pattern += "|[\u4e00-\u9fff]\s|[\u4e00-\u9fff]\s+|[\u4e00-\u9fff]\t"
        pattern = re.compile(pattern)
        pattern = pattern.findall(jpText)
        # print(pattern)
        for pat in pattern:
            replace = pat.replace(' ','')
            jpText = jpText.replace(pat, replace)
            
        # jpText = jpText.replace(' ','')
        print(jpText)
        # jpText = jpText.replace(' ','')
        jpParseTxt = parse.segmentasiTeks(jpText)

        # pprint(jpParseTxt)
        print()
        count_kata = -1
        for word in jpParseTxt:
            pattern2 = re.compile("[0-9]+|[a-zA-Z]+\'*[a-z]*")
            pattern2 = pattern2.findall(word[0])
            if pattern2:
                jpDiv.append(word[0]+' ')
                continue
            if (word[4] == 'symbol'):
                jpDiv.append(word[0]+' ')
                continue
            count_kata += 1
            jpP = self.jpHtml.new_tag('p')
            jpP['class'] = 'jisho'
            w = self.jpHtml.new_tag("ruby")
            kata = word[0]
            con = False
            jpP['data-konjugasi'] = ''
            jpP['data-kelas'] = ''
            jpP['data-katadasar'] = ''
            jpP['data-indekskata'] = str(count_kata)

            if(word[2]):
                # self.dataKamus.append(self.kamus.cariKata(word[2][0]))
                self.threads[count_kata] = CallApiThread(count_kata, word[2][0], self.kamus)
                self.threads[count_kata].start()
                self.threads[count_kata].data_kamus.connect(self.getDataKamus)
                for lemma in word[2]:
                    if (jpP['data-katadasar']):
                        jpP['data-katadasar'] += ','+lemma
                    else:
                        jpP['data-katadasar'] += lemma
                

            if(word[3]):
                for conj in word[3]:
                    if (jpP['data-konjugasi']):
                        jpP['data-konjugasi'] += ','+conj
                    else:
                        jpP['data-konjugasi'] += conj
            
            if(word[4]):
                if (jpP['data-kelas']):
                    jpP['data-kelas'] += ','+word[4]
                else:
                    jpP['data-kelas'] += word[4]
            
            # data access helper:
            # word[1][0] -> kanji
            # word[1][1] -> reading
            # kanji         - reading
            # word[1][0][0] - word[1][1][0]
            if word[1]: # check if kanji exist in the data
                temp_word = word[0]
                temp_kanji = word[1][0]
                temp_read = word[1][1]
                # print(temp_word, temp_kanji, temp_read)
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
                    temp_w = ''
                    if 0x4e00 < k_code <= 0x9fff:
                        # if the last letter is not a kanji,
                        # this will close the last rb tag
                        if con:
                            rt = self.jpHtml.new_tag("rt")
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
                        rb = self.jpHtml.new_tag("rb")
                        rb['class'] = 'kanji'
                        rb.append(temp_kanji[k_index])
                        rt = self.jpHtml.new_tag("rt")
                        rt['class'] = 'reading'
                        rt.append(parse.convKanaRo(temp_read[k_index], 'hiragana'))
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
                    rt = self.jpHtml.new_tag("rt")
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

            else:
                jpP.append(kata)

            jpDiv.append(jpP)
        # print(jpText)
        # return
        tlTxt = self.tl.translate(jpText,'bing','id')
        # tlDiv.append(tlTxt)

        self.setText(jpDiv, tlTxt)
        # Menunggu seluruh text dan class load sepenuhnya
        self.jpTxt.loadFinished.connect(self.clickableText)

        ###should i run jishoReq here instead?####

    def clickableText(self, ok):
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
                    if (ruby){
                        //p -> ruby -> rb
                        var kanji_temp = ruby.querySelectorAll('rb.kanji');
                        var kanji = ''
                        for (let i = 0; i < kanji_temp.length; i++) {
                            if (kanji) {
                                kanji += ',' + kanji_temp[i].textContent;
                            }else {
                                kanji += kanji_temp[i].textContent;
                            }                           
                        }
                        //p -> ruby -> rt
                        var reading_temp = ruby.querySelectorAll('rt.reading');
                        var reading = ''
                        for (let i = 0; i < reading_temp.length; i++) {
                            if (reading) {
                                reading += ',' + reading_temp[i].textContent;
                            }else {
                                reading += reading_temp[i].textContent;
                            }
                        }
                    }else{
                        var kanji = ''
                        var reading = ''
                    }

                    //word data helper
                    var lemma = element.dataset.katadasar;
                    if (!lemma) {
                        lemma = ''
                    }
                    var konjugasiData = element.dataset.konjugasi;
                    if (!konjugasiData) {
                        konjugasiData = ''
                    }
                    var kelasData = element.dataset.kelas;
                    if (!kelasData) {
                        kelasData = ''
                    }
                    var indeksKataData = element.dataset.indekskata;
                    if (!indeksKataData) {
                        indeksKataData = ''
                    }
                    node = element.querySelectorAll("ruby");
                    var japaneseWord = '';
                    for (let i = 0; i < node.length; i++) {
                        let nod = node[i].cloneNode(true)
                        let rt = nod.querySelector("rt");
                        nod.removeChild(rt);
                        japaneseWord += nod.textContent;
                    }
                    rect = element.getBoundingClientRect();
                    rects.push(rect);
                        
                    pyweb.tampilDetailKata(japaneseWord, [rect.right, rect.bottom, rect.left, rect.top], kanji, reading, lemma, konjugasiData, kelasData, indeksKataData);

                    console.log('tes')
                    
                });
            });
            """
            self.jpTxt.page().runJavaScript(js)

    def getDataKamus(self, index, data):
        self.dataKamus[index] = data
        pass

    # jika fungsi memiliki parameter, typedata harus ditentukan pada @pyqtSlot
    # jika ingin passing dengan class, makah class harus menginherit QObject
    @pyqtSlot(str, list, str, str, str, str, str, str)
    def tampilDetailKata(self, word, rect, kanji, reading, lemma_dat, conj_dat, class_dat, indeks):
        # print(self.viewJp.mapToGlobal(QPoint(x,y)))
        print('word : ', word, '\nkanji : ', kanji, '\nreading : ', reading, '\nlemma : ', lemma_dat, '\nconj_dat : ', conj_dat, '\nclass_dat : ', class_dat, '\nindex : ', indeks, '\n')

        kanji = kanji.split(',')
        lemma_dat = lemma_dat.split(',') # [kanji, reading]
        conj_dat = conj_dat.split(',')
        indeks = int(indeks)
        rect = [int(x) for x in rect]

        self.globTxtPos = self.jpTxt.mapToGlobal(QPoint(rect[0],rect[1]))
        self.globTxtRect = QRect(self.globTxtPos.x(), self.globTxtPos.y(), rect[0] - rect[2], rect[1] - rect[3])

        # if (kanji and reading):
        #     self.kamus.search_jisho()

        self.kamus.movePanel(self.globTxtPos.x(), self.globTxtPos.y())
        try:
            if self.dataKamus[indeks]:
                self.kamus.tampilKamus2(word, kanji, reading, lemma_dat, conj_dat, class_dat, self.dataKamus[indeks])
        except Exception as e:
            print("gagal")
            self.kamus.show()
            self.setFocus()
            self.showKamus = True
            # while not self.dataKamus[indeks]:
            #     if self.dataKamus[indeks]:
            #         self.kamus.tampilKamus2(word, kanji, reading, lemma_dat, conj_dat, class_dat, self.dataKamus[indeks])
            #         break
                # time.sleep(0.01)
        else:
            self.kamus.show()
            self.setFocus()
            self.showKamus = True
    
# for javascript debugging purpose only
class CustomWebEnginePage(QWebEnginePage):
    # override print console js untuk debugging
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # Override the JavaScriptConsoleMessage method
        print(f"JavaScript Console Message: Level {level}, Message: {message}, Line Number: {lineNumber}, Source ID: {sourceID}")

# multi-thread untuk meminta data kamus tanpa menunggu satu per satu data selesai
class CallApiThread(QThread):

    data_kamus = pyqtSignal(int, list)
    def __init__(self, index, word, kamus : Dict):
        super(CallApiThread, self).__init__()
        self.index = index
        self.word = word
        self.kamus = kamus

    def run(self):
        data = self.kamus.cariKata(self.word)
        self.data_kamus.emit(self.index, data)
        pass

    def stop(self):
        self.terminate()
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = TextScreen()
    
    screen.txtProcessing()
    screen.show()
    app.exec_()