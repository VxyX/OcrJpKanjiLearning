from __future__ import annotations
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import Qt, QUrl, pyqtSlot
from bs4 import BeautifulSoup
from pprint import pprint #debugging
import sys
import requests


from parsing import Parse
from typing import TYPE_CHECKING


# cwd = os.getcwd()  # Get the current working directory (cwd)
# files = os.listdir(cwd)  # Get all the files in that directory
# print("Files in %r: %s" % (cwd, files))

class Kamus(QWidget):
    def __init__(self, bookmarkPage, kamus_lang='en', x=100, y=100):
        super(Kamus, self).__init__()

        self.kamus_lang = kamus_lang
        self.bookmarkPage = bookmarkPage
        if self.kamus_lang == 'id':
            from translate import Translate
            self.tl = Translate()
        self.kanjivg = None
        self.word = None
        self.meanings = None
        self.part_of_speech = None
        self.jlpt_lv = None
        self.jisho_dat = None
        self.tooglebukmarkOnetime = False

        self.tag1_dict = {
            "usually written using kana alone": 'uk'
        }

        self.tag1_dict_id = {
            "usually written using kana alone": 'biasanya ditulis dengan kana saja'
        }

        self.tag2_dict = {
            "ichidan verb": 'v1',
            "godan verb with 'u' ending": 'v5u',
            "godan verb with 'ku' ending": 'v5k',
            "godan verb with 'gu' ending": 'v5g',
            "godan verb with 'su' ending": 'v5s',
            "godan verb with 'tsu' ending": 'v5t',
            "godan verb with 'nu' ending": 'v5n',
            "godan verb with 'bu' ending": 'v5b',
            "godan verb with 'mu' ending": 'v5m',
            "godan verb with 'ru' ending": 'v5r',
            "godan verb with 'ru' ending (irregular verb)": 'v5r-i',

            "suffix": 'suf',
            "noun": 'n',
            "noun, used as a suffix": 'n-suf',
            "suru verb": 'vs',
            "i-adjective (keiyoushi)": 'i-adj',
            "wikipedia definition": 'wiki',
            "computing": 'comp',
            "transitive verb": 'vt',
            "intransitive verb": 'vi'
        }

        self.tag2_dict_id = {
            "ichidan verb": 'kata kerja ichidan',
            "godan verb with 'u' ending": "kata kerja godan dengan akhiran 'u'",
            "godan verb with 'ku' ending": "kata kerja godan dengan akhiran 'ku'",
            "godan verb with 'gu' ending": "kata kerja godan dengan akhiran 'gu'",
            "godan verb with 'su' ending": "kata kerja godan dengan akhiran 'su'",
            "godan verb with 'tsu' ending": "kata kerja godan dengan akhiran 'tsu'",
            "godan verb with 'nu' ending": "kata kerja godan dengan akhiran 'nu'",
            "godan verb with 'bu' ending": "kata kerja godan dengan akhiran 'bu'",
            "godan verb with 'mu' ending": "kata kerja godan dengan akhiran 'mu'",
            "godan verb with 'ru' ending": "kata kerja godan dengan akhiran 'ru'",
            "godan verb with 'ru' ending (irregular verb)": "kata kerja godan dengan akhiran 'ru' (kata kerja iregular)",

            "suffix": "awalan",
            "noun": "nomina",
            "noun, used as a suffix": 'nomina, sebagai awalan',
            "suru verb": "nomina yang menjadi kata kerja dengan 'suru'",
            "i-adjective (keiyoushi)": "kata sifat bentuk 'i'",
            "wikipedia definition": 'definisi wikipedia',
            "computing": 'komputasi',
            "transitive verb": 'kata kerja transitif',
            "intransitive verb": 'kata kerja intransitif'
        }

        # load file
        self.dictHtmlFile = 'src/html/dictScreen.html'
        with open(self.dictHtmlFile, "r", encoding='utf-8') as file:
            self.dictTxt = BeautifulSoup(file, "html.parser")

        # create widget
        self.setWindowTitle('Frameless Widget Example')
        self.setGeometry(x, y, 300, 300)
        # self.setWindowFlag(Qt.WindowStaysOnTopHint)

        #create layout
        self.winLayout = QHBoxLayout()
        self.winLayout.setContentsMargins(0,0,0,0)
        self.contentVLayout = QVBoxLayout()
        

        # create webview
        self.content = QWebEngineView(self)
        self.content.setPage(CustomWebEnginePage(self.content))
        self.content.setUrl(QUrl.fromLocalFile('/'+self.dictHtmlFile))
        

        self.channel = QWebChannel()
        self.channel.registerObject('bookmark', self)
        self.content.page().setWebChannel(self.channel)

        if kamus_lang == 'both':
            self.dictHtmlFile2 = 'src/html/dictScreen2.html'
            with open(self.dictHtmlFile2, "r", encoding='utf-8') as file:
                self.dictTxt2 = BeautifulSoup(file, "html.parser")

            self.content2 = QWebEngineView(self)
            self.content2.setPage(CustomWebEnginePage(self.content2))
            self.content2.setUrl(QUrl.fromLocalFile('/'+self.dictHtmlFile2))
            

            self.channel2 = QWebChannel()
            self.channel2.registerObject('bookmark', self)
            self.content2.page().setWebChannel(self.channel2)
            self.winLayout.addWidget(self.content2)

        self.winLayout.addWidget(self.content)
        # set transparancy
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen)

        self.setLayout(self.winLayout)
        # self.show()
        # self.show()
        # self.content.loadFinished.connect(self.toogleBookmark)
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

    def clearTxt(self):
        js = f"""
        document.getElementById("word").innerHTML = ' ';
        document.getElementById("senses").innerHTML = ' ';
        document.getElementById("grammar-info").innerHTML = ' ';
        document.getElementById("myCheckbox").setAttribute('hidden', true);
        """
        self.content.page().runJavaScript(js)

    def toogleBookmark(self, ok):
        # print(ok, 'inites')
        if ok:
            js = """
            // objek harus diinisialisasi untuk menghubungkan fungsi py ke js
            if (typeof bookmark == 'undefined') {
                let bookmark;
            }
            
            new QWebChannel(qt.webChannelTransport, function (channel) {
                bookmark = channel.objects.bookmark;
            });

            const checkbox = document.getElementById('myCheckbox');
            checkbox.addEventListener('change', (event) => {
            if (event.currentTarget.checked) {
                console.log('checked');
                bookmark.addToBookmark('checked');
                checkbox.disabled = true;
                setTimeout(function(){
                    document.getElementById('add-bookmark').classList.add('fade');
                    checkbox.disabled = false;
                    },2000);
                document.getElementById('add-bookmark').classList.remove('fade');
            } else {
                console.log('not checked');
                bookmark.removeFromBookmark('unchecked');
                checkbox.disabled = true;
                setTimeout(function(){
                    document.getElementById('remove-bookmark').classList.add('fade');
                    checkbox.disabled = false;
                    },2000);
                document.getElementById('remove-bookmark').classList.remove('fade');
            }
            })
            """
            self.content.page().runJavaScript(js)
    
    @pyqtSlot(str)
    def addToBookmark(self, tes):
        # print(tes)
        # return
        if self.jisho_dat:
            jisho_dat = self.jisho_dat
            self.bookmarkPage.tambahBookmark(jisho_dat, self.kamus_lang)
        else:
            print('gaada')
            return
        # pprint(jisho_dat)
        pass
    
    @pyqtSlot(str)
    def removeFromBookmark(self, tes):
        # print(tes)
        # return
        if self.jisho_dat:
            jisho_dat = self.jisho_dat
            self.bookmarkPage.hapusBookmark(jisho_dat, self.kamus_lang)
        else:
            print('gaada')
            return
        pass

    def tampilKamus(self, word, kanjis, kanji_readings, lemma, conj, conj_form, classif, kamus_dat):
        
        jisho_dat = kamus_dat
        # print(jisho_dat)
        if not jisho_dat:
            js = f"""
            document.getElementById("word").innerHTML = 'Kata tidak ditemukan';
            """
            self.content.page().runJavaScript(js)
            return
        elif jisho_dat == 'connection':
            js = f"""
            document.getElementById("word").innerHTML = 'Connection Error';
            """
            self.content.page().runJavaScript(js)
            return
        
        self.jisho_dat = jisho_dat
        # print('masuk')
        ############# Word Display ##################
        ruby = self.dictTxt.new_tag("ruby")
        lemma_kanj = []
        if (jisho_dat[0]): # check if kanji exist in the data
            parser = Parse()
            # print("ada")
            lemma_kanj = parser.furigana(jisho_dat[0], jisho_dat[1])
            # print(lemma_kanj)
            temp_word = jisho_dat[0]
            temp_kanji = lemma_kanj[0]
            temp_read = lemma_kanj[1]
            con = False
            for char in jisho_dat[0]:
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
                    # print(temp_kanji[k_index], temp_kanji, temp_w)
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
            ruby.append(jisho_dat[1])      
        kata = str(ruby)
        # print(kata)
        # print('masuk')
        ############# Word Display ##################
        ############# Conjugation info Display ( if exist) ##################
        def __cek(infTxt):
            if 'Konjugasi pada ' in infTxt:
                        conjTxt.append(infTxt)
                        conjTxt.append(self.dictTxt.new_tag("br"))
        infTxt = ''
        conjTxt = self.dictTxt.new_tag("p")
        # print(conj, lemma, word)
        if word == lemma[0] or word == lemma[1]:
            pass
        else:
            try:
                
                if conj:
                    infTxt = 'Konjugasi pada ' + word + ' :'
                    # perubahan irregular ( irreguVerb/noun+irreguVerb)
                    if 'サ行変格,' in conj:
                        __cek(infTxt)
                        infTxt = '- kata benda menjadi kata kerja (する/suru).'
                        conjTxt.append(infTxt)
                        conjTxt.append(self.dictTxt.new_tag("br"))
                    
                    # kelompok kata kerja godan, kata dasar memiliki 9 kemungkinan bentuk akhiran
                    # if '五段' in conj:
                    #     # print(conj)
                    #     if '五段-ワア行' in conj:
                    #         infTxt +='Kelompok kata kerja Godan dengan akhiran (う/u).\t'
                    #     pass
                    if 'conj' in conj:
                        if ('conj-て,' in conj and 'conj-いる' in conj) or ('conj-てる' in conj):
                            __cek(infTxt)
                            infTxt ='- bentuk berkelanjutan (~ている/~teiru).'
                            if 'conj-てる,' in conj:
                                infTxt ='- bentuk berkelanjutan (~てる/~teru).'
                            conjTxt.append(infTxt)
                            conjTxt.append(self.dictTxt.new_tag("br"))
                            pass
                        else:
                            if 'conj-て,' in conj:
                                __cek(infTxt)
                                infTxt ='- bentuk penghubung (~て/~te).'
                                conjTxt.append(infTxt)
                                conjTxt.append(self.dictTxt.new_tag("br"))
                                pass
                            if 'conj-いる,' in conj:
                                __cek(infTxt)
                                pass
                        if 'conj-させる,' in conj:
                            __cek(infTxt)
                            infTxt ='- bentuk pasif (~させる/~saseru).'
                            conjTxt.append(infTxt)
                            conjTxt.append(self.dictTxt.new_tag("br"))
                            pass
                        if 'conj-られる,' in conj:
                            __cek(infTxt)
                            infTxt ='- ... (~られる/~rareru).'
                            conjTxt.append(infTxt)
                            conjTxt.append(self.dictTxt.new_tag("br"))
                            pass
                        if 'conj-て,' in conj:
                            __cek(infTxt)
                            pass

                    # aux verb
                    if '助動詞' in conj:
                        if '助動詞-マス,' in conj:
                            __cek(infTxt)
                            infTxt = '- bentuk formal (~ます/~masu).'
                            conjTxt.append(infTxt)
                            conjTxt.append(self.dictTxt.new_tag("br"))
                            pass
                        if '助動詞-ヌ,' in conj:
                            __cek(infTxt)
                            infTxt = '- bentuk negatif (~な/~na).'
                            conjTxt.append(infTxt)
                            conjTxt.append(self.dictTxt.new_tag("br"))
                            pass
                        if '助動詞-ナイ,' in conj:
                            __cek(infTxt)
                            infTxt = '- bentuk negatif (~ない/~nai).'
                            conjTxt.append(infTxt)
                            conjTxt.append(self.dictTxt.new_tag("br"))
                            pass
                        # is this necessary???
                        if '助動詞-デス,' in conj:
                            __cek(infTxt)
                            
                            pass
                        if '助動詞-レル,' in conj:
                            __cek(infTxt)
                            infTxt = '- bentuk pasif (~られる/~saseru).'
                            conjTxt.append(infTxt)
                            conjTxt.append(self.dictTxt.new_tag("br"))
                        if '助動詞-セル,' in conj:
                            __cek(infTxt)
                            infTxt = '- ... (~させる/~saseru).'
                            conjTxt.append(infTxt)
                            conjTxt.append(self.dictTxt.new_tag("br"))
                        if '助動詞-タイ,' in conj:
                            __cek(infTxt)
                            infTxt = '- manyatakan keinginan (~たい/~tai).'
                            conjTxt.append(infTxt)
                            conjTxt.append(self.dictTxt.new_tag("br"))
                            pass
                        if '助動詞-タ,' in conj and not ('仮定形' in conj_form):
                            __cek(infTxt)
                            infTxt = '- bentuk lampau (~た/~ta).'
                            conjTxt.append(infTxt)
                            conjTxt.append(self.dictTxt.new_tag("br"))
                            pass
                        if '助動詞-タ,' in conj and '仮定形' in conj_form:
                            __cek(infTxt)
                            infTxt = '- bentuk kondisional (jika) (~たら/~tara).'
                            conjTxt.append(infTxt)
                            conjTxt.append(self.dictTxt.new_tag("br"))
                            pass
                    
                    if conj_form:
                        if '意志推量形' in conj_form:
                            __cek(infTxt)
                            infTxt = '- bentuk ajakan (~よう/~you).'
                            conjTxt.append(infTxt)
                            conjTxt.append(self.dictTxt.new_tag("br"))

                    if 'Konjugasi pada ' in infTxt:
                        infTxt = ''
                # conjTxt.append(infTxt)
                
                # print(conjTxt)
            except Exception as e:
                print(e)
        # print('masuk')
        konjugasi = str(conjTxt)
        ############# Conjugation info Display ( if exist) ##################
        ############# Senses Display ##################
        
        if self.kamus_lang == 'both':
            senses = jisho_dat[0][3]
            senses2 = jisho_dat[1][3]
            pass
        else:
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
                        p['class'] = 'tags tag1'
                        p['title'] = tag1[0]
                        if tag1[1]:
                            p.append(tag1[1])
                        else:
                            p.append(tag1[0])
                        div_tag1.append(p)
                        pass
                
                div_tag2 = self.dictTxt.new_tag("div")
                div_tag2['class'] = 'group_tag2'
                if sense[1]:
                    # pprint(sense[1])
                    for tag2 in sense[1]:
                        p = self.dictTxt.new_tag("p")
                        p['class'] = 'tags tag2'
                        p['title'] = tag2[0]
                        if tag2[1]:
                            p.append(tag2[1])
                        else:
                            p.append(tag2[0])
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
        # print('masuk')
        
        js = f"""
        document.getElementById("word").innerHTML = '{kata}';
        document.getElementById("grammar-info").innerHTML = '{konjugasi}';
        document.getElementById("senses").innerHTML = '{senses}';
        document.getElementById("myCheckbox").removeAttribute('hidden');
        """
        if self.bookmarkPage:
            cek_kata = self.bookmarkPage.cek_kata(jisho_dat, self.kamus_lang)
            if cek_kata:
                js += """document.getElementById("myCheckbox").checked = true;"""
            else:
                js += """document.getElementById("myCheckbox").checked = false;"""
        self.content.page().runJavaScript(js)

        if not self.tooglebukmarkOnetime:
            self.toogleBookmark(True)
            self.tooglebukmarkOnetime = True
            

        if self.kamus_lang == 'both':
            kata2 = kata
            konjugasi2 = None
            js = f"""
            document.getElementById("word").innerHTML = '{kata2}';
            document.getElementById("grammar-info").innerHTML = '{konjugasi2}';
            document.getElementById("senses").innerHTML = '{senses2}';
            document.getElementById("myCheckbox").removeAttribute('hidden');
            """
            self.content2.page().runJavaScript(js)
        pass

    # Fungsi untuk mencari makna kata di Jisho menggunakan Jisho API
    def cariKata(self, word, reading=None, tag=None):

        url = f"https://jisho.org/api/v1/search/words?keyword={word}"
        if reading:
            url += f"%20{reading}"
        if tag:
            url += f"%20%23{tag}"
        # print(url)
        try:
            response = requests.get(url)
        except Exception as e:
            return 'connection'
        
        # http://jisho.org/api/v1/search/words?keyword=%23jlpt-n5
        # What i need...
        # japanese word kanji (data->[0-?]->[japanese]->[0]->[word])
        # japanese word reading hiragana (data->[0-?]->[japanese]->[0]->[reading])
        # jlpt level (data->[0-?]->[jlpt]->[])
        # word type/part of speech/kelas kata (data->sense->[0-?]->part_of_speech->[])
        # meanings (data->sense->[0-?]->english_definitions->[])

        if response.status_code == 200:
            data = response.json()
            # print()
            # print('input kata :', word)
            # print()
            # print('output data jisho:')
            # pprint(data["data"][0])
            # return
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
                temp_lang = ''
                # limit definition more than X
                limit_definition = 5
                count_sense = 0
                for sense in result["senses"]:
                    try:
                        if count_sense == limit_definition:
                            break
                        more_info = sense["tags"]
                        if sense["tags"]:
                            more_info = []
                            for one in sense["tags"]:
                                one = str.lower(one)
                                if one in self.tag1_dict:
                                    more_info.append([one, self.tag1_dict[one]])
                                else:
                                    more_info.append([one, ''])
                        # print(more_info)
                        kelas = sense["parts_of_speech"]
                        if sense["parts_of_speech"]:
                            kelas = []
                            for one in sense["parts_of_speech"]:
                                one = str.lower(one)
                                if one in self.tag2_dict:
                                    kelas.append([one, self.tag2_dict[one]])
                                else:
                                    kelas.append([one, ''])
                        
                        # testing for kamus tl indo
                        # for tl in kelas:
                        #     kelas_tl = translate.translate_text(tl,'bing','id','en')
                        meanings = sense["english_definitions"]
                        if self.kamus_lang == 'both':
                            senses.append([more_info, kelas, meanings])
                            temp_lang = 'both'
                            self.kamus_lang = 'id'
                        # for tl in meanings:
                        #     meanings_tl = translate.translate_text(tl,'bing','id','en')
                        if self.kamus_lang == 'id':
                            if more_info:
                                temp_more_info = []
                                for one in more_info:
                                    if one[0] in self.tag1_dict_id:
                                        temp_more_info.append([self.tag1_dict_id[one[0]], one[1]])
                                    else:
                                        temp_more_info.append([one[0], one[1]])
                                more_info = temp_more_info
                            # print(kelas)
                            if kelas:
                                temp_kelas = []
                                for one in kelas:
                                    if one[0] in self.tag2_dict_id:
                                        temp_kelas.append([self.tag2_dict_id[one[0]], one[1]])
                                    else:
                                        temp_kelas.append([one[0], one[1]])
                                kelas = temp_kelas
                            if meanings:
                                temp_meanings = []
                                for one in meanings:
                                    # print(one)
                                    tl_txt = self.tl.translate(one,self.kamus_lang,'en','google')
                                    if temp_meanings:
                                        if tl_txt in temp_meanings:
                                            continue
                                    temp_meanings.append(tl_txt)
                                meanings = temp_meanings
                        if temp_lang:
                            self.kamus_lang = temp_lang
                            temp_lang = ''
                        senses.append([more_info, kelas, meanings])
                        count_sense += 1
                    except Exception as e:
                        print(e)
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
        # print(f"JavaScript Console Message: Level {level}, Message: {message}, Line Number: {lineNumber}, Source ID: {sourceID}")
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Kamus(None, 'en')
    widget.show()
    search_word = 'じゃない'
    meanings = widget.cariKata(search_word)
    print(meanings)
    # print(f"Makna kata {japanese_word}: {', '.join(meanings)}")
    
    sys.exit(app.exec_())