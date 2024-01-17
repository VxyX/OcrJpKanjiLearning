import typing
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QFrame
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5 import uic
from PyQt5.QtCore import Qt, QUrl
from ast import literal_eval
from bs4 import BeautifulSoup
import sys
from pprint import pprint


from screen import ScreenCapture
from txtscreen import TextScreen
from jisho import Dict
from bookmark import BookmarkDB, BookmarkWidget
from parsing import Parse
import os


class BookmarkPage(QWidget):
    def __init__(self):
        
        super(BookmarkPage, self).__init__()

        self.mainAppRun = True
        self.isShown = False

        self.widgets = []
        self.id_kata = []
        self.checkData = []
        self.db = BookmarkDB()
        
        # load .ui file
        uic.loadUi("src/gui/mainuiWidget/BookmarkWidget.ui", self)

        self.scrollContainer = QWidget()
        self.containerLayout = QVBoxLayout()
        self.containerLayout.setContentsMargins(0,0,0,0)
        self.tampil_data()
        self.containerLayout.setAlignment(Qt.AlignTop)
        self.scrollContainer.setLayout(self.containerLayout)
        self.scrollContainer.setObjectName('coontainer')
        self.setStyleSheet('''#a{
                           border: 1px solid rgba(0,0,0,0.3);
                           border-left: none;
                           border-right: none;
                           border-top: none;
        }''')

        self.scrollLayout = QVBoxLayout()
        self.scrollLayout.addWidget(self.scrollContainer)
        self.scrollWidget.setLayout(self.scrollLayout)

        self.hapusBtn.clicked.connect(self.hapusBtnEvent)
        self.hapusBtn.setEnabled(False)
        self.kembaliBtn.clicked.connect(self.kembaliBtnEvent)

        self.detailHtmlFile = 'src/html/detailBookmark.html'
        with open(self.detailHtmlFile, "r", encoding='utf-8') as file:
            self.detailTxtHtml = BeautifulSoup(file, "html.parser")

        self.content = QWebEngineView(self)
        # self.content.setPage(CustomWebEnginePage(self.content))
        self.content.setUrl(QUrl.fromLocalFile('/'+self.detailHtmlFile))

        self.detailWidgetLayout = QVBoxLayout()
        self.detailWidgetLayout.addWidget(self.content)
        self.detailWidget.setLayout(self.detailWidgetLayout)

    def hapusBtnEvent(self):
        i = 0
        dat = len(self.id_kata)
        while i < dat:
            if self.checkData[i].isChecked():
                print(self.id_kata[i])
                self.db.delete_bookmark(self.id_kata[i])
                self.widgets[i].deleteLater()
                del self.widgets[i]
                del self.checkData[i]
                del self.id_kata[i]
                i = i - 1
                dat = dat - 1
            i = i + 1
            pass
        print(len(self.checkData), len(self.id_kata), len(self.widgets))
        pass
    
    def kembaliBtnEvent(self):
        self.BookmarkPanel.setCurrentIndex(0)
        pass

    def tambahBookmark(self, jisho_dat, bahasa):
        temp = self.db.insert_bookmark(jisho_dat, bahasa)
        if temp:
            id_kata, kata, hiragana, romaji, makna = temp
            self.tambahWidget(id_kata, kata, hiragana, romaji, makna)
        pass

    def tambahWidget(self, id_kata, kata, hiragana, romaji, makna_dat):
        cont = BookmarkWidget()
        self.checkData.append(cont.checkBox)
        self.id_kata.append(id_kata)
        # lambda a, b=2: func(a, b)
        cont.detailTxt.mousePressEvent = lambda event, id_kata=id_kata: self.tampilDetail(event, id_kata)
        cont.checkBox.stateChanged.connect(self.checkCheckbox)
        cont.kata.setText(kata)
        cont.caraBaca.setText(hiragana+' ('+romaji+')')
        # print(row)
        makna = makna_dat
        # makna = makna[0] + ",..."
        makna = ', '.join(makna)
        if len(makna) > 10:
                makna = makna[:10] + '...'
        # print(makna)
        cont.makna.setText(makna)
        self.widgets.append(cont)
        self.containerLayout.addWidget(cont)
        pass

    def tampilDetail(self, event, id_kata):
        # print(id_kata)
        kata, makna = self.db.get_data(id_kata)
        kata = kata[0]
        # pprint(makna)
        self.tampilDetailData(kata, makna)
        self.BookmarkPanel.setCurrentIndex(1)
        pass

    def tampilDetailData(self, kata_dat, makna_dat):
        ############# Word Display ##################
        ruby = self.detailTxtHtml.new_tag("ruby")
        lemma_kanj = []
        if (kata_dat[2]): # check if kanji exist in the data
            parser = Parse()
            # print("ada")
            lemma_kanj = parser.furigana(kata_dat[2], kata_dat[3])
            # print(lemma_kanj)
            temp_word = kata_dat[2]
            temp_kanji = lemma_kanj[0]
            temp_read = lemma_kanj[1]
            con = False
            for char in kata_dat[2]:
                # this will skip if the current letter not matching the temp word letter
                # this helps to fix problems if theres more than 1 letter/kanji inside temp word/kanji
                # so it can skip the current leter
                if temp_word:
                    if char != temp_word[0]:
                        continue
                else:
                    break

                k_code = ord(char)
                temp_w = ''
                if 0x4e00 <= k_code <= 0x9fff:
                    # if the last letter is not a kanji,
                    # this will close the last rb tag
                    if con:
                        rt = self.detailTxtHtml.new_tag("rt")
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
                    rb = self.detailTxtHtml.new_tag("rb")
                    rb['class'] = 'kanji'
                    rb.append(temp_kanji[k_index])
                    # print(temp_kanji[k_index], temp_kanji, temp_w)
                    rt = self.detailTxtHtml.new_tag("rt")
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
                    rt = self.detailTxtHtml.new_tag("rt")
                    ruby.append(rt)
                    con = False
        else:
            ruby.append(kata_dat[3])      
        kata = str(ruby)
        # print(kata)
        # print('masuk')
        ############# Word Display ##################
        ############# Senses Display ##################
        # def tampilSense(jisho_dat):
        tag1_dict = []
        tag2_dict = []
        div_list = []
        for sense in makna_dat:
            div_sense = self.detailTxtHtml.new_tag("div")
            div_sense['id'] = 'sense' #grouping tags and meanings

            div_tags = self.detailTxtHtml.new_tag("div")
            div_tags['id'] = 'tags'

            div_meanings = self.detailTxtHtml.new_tag("div")
            div_meanings['id'] = 'meanings'

            div_tag1 = self.detailTxtHtml.new_tag("div")
            div_tag1['class'] = 'group_tag1'
            
            if sense[1]:
                sense1 = literal_eval(sense[1])
                for tag1 in sense1:
                    p = self.detailTxtHtml.new_tag("p")
                    p['class'] = 'tags tag1'
                    p['title'] = tag1[0]
                    if tag1[1]:
                        p.append(tag1[1])
                    else:
                        p.append(tag1[0])
                    div_tag1.append(p)
                    pass
            
            div_tag2 = self.detailTxtHtml.new_tag("div")
            div_tag2['class'] = 'group_tag2'
            if sense[2]:
                sense2 = literal_eval(sense[2])
                for tag2 in sense2:
                    p = self.detailTxtHtml.new_tag("p")
                    p['class'] = 'tags tag2'
                    p['title'] = tag2[0]
                    if tag2[1]:
                        p.append(tag2[1])
                    else:
                        p.append(tag2[0])
                    div_tag2.append(p)
            # print('masuk')
            ul = self.detailTxtHtml.new_tag("ul")
            if sense[3]:
                sense3 = literal_eval(sense[3])
                for meaning in sense3:
                    li = self.detailTxtHtml.new_tag("li")
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
        # print('masuk')
        ############# Senses Display ##################
        js = f"""
        document.getElementById("word").innerHTML = '{kata}';
        document.getElementById("senses").innerHTML = '{senses}';
        """
        self.content.page().runJavaScript(js)

            
        pass

    def checkCheckbox(self, state):
        # if state == 2:  # Qt.Checked
        #     self.checkData[self.sender()] = True
        # else:
        #     self.checkData[self.sender()] = False

        if any(a.isChecked() for a in self.checkData):
            self.hapusBtn.setEnabled(True)
        else:
            self.hapusBtn.setEnabled(False)
        print(len(self.checkData), len(self.id_kata), len(self.widgets))
        pass
    
    def tampil_data(self):
        # print(rows)
        kata, makna = self.db.showall_bookmark()

        for i in range(len(kata)):
            self.tambahWidget(kata[i][0], kata[i][1], kata[i][3], kata[i][4], makna[i])
            pass
        pass

    def closeEvent(self, event:QCloseEvent) -> None:
        self.isShown = False
        self.hide()
        event.ignore()
        pass

################## Translate Menu ##################
class TranslatePage(QWidget):
    def __init__(self, bookmarkPage:BookmarkPage):
        super(TranslatePage, self).__init__()

        # load .ui file
        uic.loadUi("src/gui/mainuiWidget/TranslateWidget.ui", self)

        self.isStart = False
        self.bookmarkPage = bookmarkPage

        # 
        self.dicLang.setItemData(0, 'id')
        self.dicLang.setItemData(1, 'en')
        self.transLang.setItemData(0, 'id')
        self.transLang.setItemData(1, 'en')
        self.transLang.setItemData(2, 'both')

        self.kamus_lang = self.transLang.currentData()
        self.translate_lang = self.dicLang.currentData()
        print(self.kamus_lang, self.translate_lang)

        self.transLang.currentIndexChanged.connect(self.cekBahasaTerjemahan)
        self.dicLang.currentIndexChanged.connect(self.cekBahasaKamus)
        self.dicLang.setEnabled(False)
        self.checkDiffLang.stateChanged.connect(self.cekBedaBahasa)
        self.startBtn.clicked.connect(self.startScreen)

    def startScreen(self):

        if not self.isStart:
            if self.bookmarkPage:
                self.kamusPage = Dict(self.bookmarkPage, self.kamus_lang)
            else:
                return
            if self.kamusPage:
                self.txtScreen = TextScreen(self.kamusPage, self.translate_lang)
            else:
                return
            if self.txtScreen:
                self.screenshot = ScreenCapture(self.txtScreen)
            else:
                return
            
            self.isStart = True
            self.startBtn.setText("Stop")
            
            # print('click')
            # Thread(target=self.screen.show()).start()
            # Thread(target=self.textScreen.show()).start()
        else:
            self.isStart = False
            
            self.txtScreen.clearTxt()
            self.screenshot.closeScreen()
            self.startBtn.setText("Start")
            # Thread(target=self.screen.close()).start()
            # Thread(target=self.textScreen.close()).start()
            return
        
    def cekBedaBahasa(self, state):
        if state == 2:  # Qt.Checked
            # print('Checkbox dicentang')
            self.dicLang.setEnabled(True)
        else:
            # print('Checkbox tidak dicentang')
            i = self.transLang.currentIndex()
            self.dicLang.setCurrentIndex(i)
            # print(i)
            self.dicLang.setEnabled(False)
    
    def cekBahasaKamus(self, index):
        # print(self.trasLang.currentData())
        self.kamus_lang = self.dicLang.currentData()
        print(self.kamus_lang)

    def cekBahasaTerjemahan(self, index):
        # print(self.trasLang.currentData())
        self.translate_lang = self.transLang.currentData()
        print(self.translate_lang)
        if (self.checkDiffLang.checkState() == 0):
            self.dicLang.setCurrentIndex(index)

    def close(self) -> bool:
        self.kamusPage.close()
        self.txtScreen.close()
        self.screenshot.close()
        return super().close()
################## Translate Menu ##################


class AboutPage(QWidget):
    def __init__(self):
        super(AboutPage, self).__init__()

        # load .ui file
        uic.loadUi("src/gui/mainuiWidget/InfoWidget.ui", self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    jisho_dat = '''['泳ぐ', 'およぐ', ['jlpt-n5'], [[[], [["godan verb with 'gu' ending", 'v5g'], ['intransitive verb', 'vi']], ['to swim']], [[], [["godan verb with 'gu' ending", 'v5g'], ['intransitive verb', 'vi']], ['to struggle through (a crowd)']], [[], [["godan verb with 'gu' ending", 'v5g'], ['intransitive verb', 'vi']], ["to make one's way through the world", 'to get along (in life)']], [[], [["godan verb with 'gu' ending", 'v5g'], ['intransitive verb', 'vi']], ['to totter', "to lose one's balance"]]]]'''
    a = BookmarkPage()
    a.show()
    a.tambahBookmark(literal_eval(jisho_dat), 'id')
    app.exec_()

        