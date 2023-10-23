import MeCab
import sqlite3
import sys
import pytesseract
from PIL import Image
from pprint import pprint

class Parse():
    def __init__(self):
        # jp dictionary for MeCab
        self.unidic = r'D:\\Bakup\\Materi\\Semester9\\Skripsi\\program\\orcjplearning\\dic\\unidic'
        self.ipadic = r'D:\\Bakup\\Materi\\Semester9\\Skripsi\\program\\orcjplearning\\dic\\ipadic'

        self.tagger = MeCab.Tagger(f"-d {self.unidic}")
        pass
    
    def jpParse1(self, text):
        # testing beberapa kalimat
        # text = "行ってきましたか"
        # text = "あんたと話しました。なぜこんな風にかしら"
        # text = "自分の両親をこんな風にを扱うなんて、彼は気が狂っているに違いない。"
        # text = "こんな風に。こんなことがあるなんて"
        # text = "再び、彼は放浪者となって、彼はある日、兄の家にたどり着いた。"
        # text = "こんな、そんな、あんな"
        # text = "アパートの壁が薄いので、隣の部屋の人のいびきまで聞こえてきて、気になって眠れない。"
        # text = "私の両親は、田舎で農業を営んでいる"
        # text = "聞こえる.聞こえない.聞こえます.聞こえません.聞こえた.聞こえなかった.聞こえました.聞こえませんでした.聞こえて.聞こえなくて.聞こえられる.聞こえられない.聞こえさせる.聞こえさせない.聞こえさせられる.聞こえさせられない.聞こえろ.聞こえるな"
        # text = "聞えるんだよ"
        # text = text

        result = self.tagger.parse(text) #or parseNBest(n, text)
        result = result.splitlines() #splitLines untuk pengelompokan tabel berdasarkan kata yang displit MeCab

        # inisialisasi data untuk menampung hasil MeCab
        data = []
        # pengelompokan berdasarkan tabel output MeCab
        for line in result:
            values = line.split('\t') 
            if (values == ['EOS']):
                continue
            data.append(values)
        print(data)

        # inisialisasi sebelum dilakukan parsing
        conj = False
        # dataiter = iter(data)
        next_data_row = None
        kelompokKata = []
        kelompokKataKerja = []
        inputKata = False
        kata = ''
        kataasli = ''
        skip = False

        for i in range(len(data)):
            # if skip:
            #     skip = False
            #     continue
            if (data[i][5]):
                kelompokKataKerja.append(data[i][5])
                if ("動詞-一般" in data[i][4]):
                    kataasli = data[i][3]


            if ('サ変可能' in data[i][4]):
                # conjVerb = True
                if ('非自立可能' in data[i+1][4] or '接尾辞' in data[i+1][4]):
                    conj = True

            # combine verb 連用形 (renkyoukei/continuous form), 連体詞 (rentaishi/pre-noun adjectival/pronomina)
            # 助詞-準体助詞 ()
            if ('連用形' in data[i][6] or '連体詞' in data[i][4] or '助詞-準体助詞' in data[i][4] or '未然形' in data[i][6]):
                conj = True
                try:
                    if ('連体詞' in data[i][4] and ('名詞-普通名詞-一般' in data[i+1][4] or '名詞' not in data[i+1][4])):
                        conj = False
                except IndexError as e:
                    pass
            
            # fix combined phrase with non-independent verb and final-form also not actially verb
            # ex : ある can be verb or pronomina
            try:
                if ('非自立' in data[i+1][4] and not data[i+1][5]):
                    conj = True 
            except IndexError as e:
                pass
            # if ('助動詞' in data[i][4]):
            #     # kata += data[0]
            #     conjVerb = False
            #     # next_data_row = next(dataiter)
            #     try:
            #         if ('助動詞' in data[i+1][4]):
            #             conjVerb = True
            #     except IndexError as e:
            #         pass
            
            # print(conjVerb, inputkata, data[i][0])
            if conj:
                inputKata = False
                kata += data[i][0]
                try:
                    if ('助動詞' in data[i][4]):
                        # kata += data[0]
                        conj = False
                        inputKata = True
                        # fix multiple auxverb and continuous form
                        if ('助動詞' in data[i+1][4] or '接続助詞' in data[i+1][4]):
                                conj = True
                                inputKata = False

                    # fix adjective and adverb combination
                    if ('形状詞' in data[i][4] or '副詞' in data[i][4]):
                        if ('助動詞' in data[i+1][4]):
                            conj = True
                            inputKata = False
                        else :
                            conj = False
                            inputKata = True
                            
                    # fix noun suffix like 者 (orang) -> 冒険者 (Petualang) 医者 (Dokter)
                    if ('接尾辞' in data[i][4] and 'サ変可能' in data[i-1][4]):
                        inputKata = True
                        conj = False

                    # fix conjuctive particle -Te that has 非自立 (non-independent) form on the next iteration
                    # ex : 聞こえてきて [kikoe(verb -> base = 聞く) -te(particle) -ki(non-independent) -te(particle)]
                    if ('接続助詞' in data[i][4]):
                        if ('非自立' not in data[i+1][4]):
                            conj = False
                            inputKata = True

                    if ('非自立可能' in data[i][4]):
                        inputKata = True
                        conj = False
                        if ('助動詞' in data[i+1][4] or '非自立可能' in data[i+1][4] or '接続助詞' in data[i+1][4]):
                            # kata += data[0]
                            conj = True
                            inputKata = False

                    if ('終助詞' in data[i][4]):
                        conj = False
                        inputKata = True
                    
                except IndexError as e:
                    inputKata = True
                # if next_data_row:
                #     if ('終止形' in next_data_row[6]):
                #         conjVerb = False
                #         inputkata = True
                #     kata += next_data_row[0]
                #     next_data_row = None
            else :
                inputKata = True
                kata += data[i][0]
            
            # print(conjVerb, inputkata, kata)
            if inputKata:
                temp = kata
                if kataasli:
                    temp = [temp, kataasli]
                if kelompokKataKerja:
                    temp = [temp, kelompokKataKerja]
                kelompokKata.append(temp)
                kata = ''
                kataasli = ''
                kelompokKataKerja = []
        #############END FOR LOOP#####################

        pprint(kelompokKata)
        return kelompokKata
    
if (__name__ == "__main__"):
    parse = Parse()
    parse.jpParse1("自分の両親をこんな風にを扱うなんて、彼は気が狂っているに違いない。")