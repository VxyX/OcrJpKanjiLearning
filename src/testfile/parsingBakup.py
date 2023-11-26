import MeCab
import sqlite3
import sys
import pytesseract
from PIL import Image
from pprint import pprint
import romkan

# to_u = ['ぅ', 'う', 'ぉ', 'お', 'く', 'ぐ', 'こ', 'ご', 'す', 'ず', 'そ', 'ぞ', 'つ', 'づ', 'と', 'ど', 'の', 'ふ', 'ぶ', 'ぷ', 'ほ', 'ぼ', 'ぽ', 'も', 'よ', 'ょ']
# to_i = ['ぇ', 'え', 'け', 'げ', 'せ', 'ぜ', 'て', 'で', 'ね', 'へ', 'べ', 'ぺ' 'め']

class Parse():
    def __init__(self):
        # jp dictionary for MeCab
        self.unidic = r'D:\\Bakup\\Materi\\Semester9\\Skripsi\\program\\orcjplearning\\dic\\unidic'
        self.ipadic = r'D:\\Bakup\\Materi\\Semester9\\Skripsi\\program\\orcjplearning\\dic\\ipadic'

        self.tagger = MeCab.Tagger(f"-d {self.unidic}")
        pass
    
    def furigana(self, text, jenis_huruf='hiragana'or'katakana'or'romaji'):
        txt = text
        new_txt = ''
        if jenis_huruf == 'romaji':
            new_txt = romkan.to_roma(text)
        else:
            for char in txt:
                char_code = ord(char)
                if jenis_huruf == 'hiragana':
                    # Periksa apakah karakter bukan hiragana
                    if not 0x3040 <= char_code <= 0x309F:
                        # Periksa apakah karakter adalah katakana
                        if 0x30A0 <= char_code <= 0x30FF:
                            # Kode hiragana adalah kode katakana - 96
                            hiragana_code = char_code - 96 
                            hiragana_character = chr(hiragana_code)
                            new_txt += hiragana_character
                    else:
                        # Jika bukan karakter katakana, tambahkan karakter aslinya
                        new_txt += char

                if jenis_huruf == 'katakana':
                    if not 0x30A0 <= char_code <= 0x30FF:
                        if 0x3040 <= char_code <= 0x309F:
                            # Kode hiragana adalah kode katakana - 96
                            katakana_code = char_code + 96 
                            katakana_character = chr(katakana_code)
                            new_txt += katakana_character
            

        return new_txt

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
        print('Input : \n', text, '\n')
        result = self.tagger.parse(text) #or parseNBest(n, text)
        print('Output : \n', result)
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
        # exit()
        # inisialisasi sebelum dilakukan parsing
        conj = False
        # dataiter = iter(data)
        next_data_row = None
        kelompokKata = []
        kelompokKataKerja = []
        inputKata = False
        kata = ''
        katadasar = []
        bantuan = ''
        kanji = []
        skip = False
        combine_count = 0

        for i in range(len(data)):
            combine_count += 1
            # if skip:
            #     skip = False
            #     continue

            ########## cek apakah terdapat kanji ############
            kanji_check = data[i][0]
            kanjilist = list(kanji_check)
            for char in kanjilist:
                kanjiCode = ord(char)
                if (kanjiCode > 0x4e00 and kanjiCode <= 0x9fff):
                    kanjilist2 = list(kanji_check)
                    kanalist = list(data[i][1])
                    hiraganalist = [] # will replace the katakana reading to hiragana
                    temp_count = 0
                    for x in range(len(kanalist)):
                        c = kanalist[x]
                        if (c == 'ー'):
                            # mengubah pelafalan vokal panjang menjadi huruf yang sesuai
                            if hiraganalist:
                                
                                try:
                                    c_index = kanalist.index(c)
                                    c = data[i][2][c_index]
                                except IndexError as e:
                                    c_index = data[i][0].index(hiraganalist[-1])
                                    c = data[i][0][c_index+1]
                        c = ord(c)
                        if 0x30A0 <= c <= 0x30FF:
                            # Kode hiragana adalah kode katakana - 96
                            hiragana_code = c - 96 
                            hiragana_char = chr(hiragana_code)
                            hiraganalist.append(hiragana_char)
                    # print(kanjilist2)

                    # better kanji and reading separation
                    new_kList = []
                    new_hiList = []
                    if hiraganalist:
                        for c in kanjilist:
                            c_code = ord(c)
                            # print(c , c_code)
                            if (0x3040 <= c_code <= 0x309F):
                                for c1 in hiraganalist:
                                    # check if reading and word have the same char
                                    if (c == c1):
                                        # check if 
                                        h_index = hiraganalist.index(c1)
                                        if (h_index != 0):
                                            str_hi = ''
                                            for h in range(h_index):
                                                str_hi += hiraganalist[h]
                                            new_hiList.append(str_hi)
                                        # this will remove the current word and earlier index
                                        # to prevent checking the same character
                                        hiraganalist = hiraganalist[h_index+1:]
                                        kanjilist2.remove(c1)
                                        
                                        # print(hiraganalist)
                                        break
                            else:
                                new_kList.append(c)
                    # print(kanjilist2, hiraganalist)
                    # str_kanjilist = ''.join(kanjilist2)
                    # str_hiraganalist = ''.join(hiraganalist)
                    # print(str_kanjilist, str_hiraganalist)
                    if (not new_hiList):
                        str_hiraganalist = ''.join(hiraganalist)
                        new_hiList = [str_hiraganalist]
                        str_kanjilist = ''.join(new_kList)
                        new_kList = [str_kanjilist]

                    if (kanji):
                        kanji[0].extend(new_kList)
                        kanji[1].extend(new_hiList)
                    else :
                        temp = [new_kList, new_hiList]
                        kanji += temp
                    # print(kanji)
                    break
            ########## cek apakah terdapat kanji ############

            # cek tipe kelompok kata kerja
            if (data[i][5]):
                kelompokKataKerja.append(data[i][5])
                # 動詞 (youshi) = kata kerja
                # 容詞 (doushi) = kata sifat
                if ((("動詞-一般" in data[i][4]) 
                    or ("容詞-一般" in data[i][4]) 
                    or ("動詞-非自立可能" in data[i][4])) and '連体形' not in data[i][6]):
                    if not katadasar:
                        katadasar = [data[i][3], data[i][2]]


            # if ('サ変可能' in data[i][4]):
            #     # conjVerb = True
            #     try:
            #         if ('非自立可能' in data[i+1][4] or '接尾辞' in data[i+1][4]):
            #             conj = True
            #     except :
            #         pass

            
            
            # fix combined phrase with non-independent verb and final-form also not actially verb
            # ex : ある can be verb or pronomina
            try:
                # combine verb 連用形 (renkyoukei/continuous form), 連体詞 (rentaishi/pre-noun adjectival/pronomina)
                # 助詞-準体助詞 ()?
                if ('連用形' in data[i][6] 
                    or '連体詞' in data[i][4] 
                    or '未然形' in data[i][6]):
                    conj = True
                    if (('連体詞' in data[i][4] and 
                        ('名詞-普通名詞-形状詞可能' not in data[i+1][4] or '名詞' not in data[i+1][4])) or
                        ('形容詞' in data[i][4] and ('名詞' in data[i+1][4] or '形容詞' in data[i+1][4] or '動詞' in data[i+1][4]))):
                        conj = False
                # print(conj, inputKata, data[i][0])
                if ('動詞' in data[i][4] or '容詞' in data[i][4] or '副詞' in data[i][4]):
                    if (('接続助詞' in data[i+1][4]) or
                        ('動詞' in data[i+1][4] and ('終止形' in data[i+1][6] or '未然形' in data[i+1][6] or '連体形' in data[i+1][6]))):
                        conj = True
                        pass
                # print(conj, inputKata, data[i][0])
                if ('非自立' in data[i+1][4] and not data[i+1][5]):
                    conj = True 
                # print(conj, inputKata, data[i][0])
                if (data[i][3] == 'に' and '文語' in data[i+1][5]):
                    conj = True
                # print(conj, inputKata, data[i][0])
                if (('非自立' in data[i+1][4] and not ('動詞' in data[i][4] or '形容詞' in data[i][4])) 
                    or ('接尾辞' in data[i+1][4] and not data[i+1][5])):
                    conj = True 
                    # prevent combining word if current word is particle
                    # and not particle that attaches to a phrase
                    if (('助詞' in data[i][4] and ('準体助詞' not in data[i][4] and '接続助詞' not in data[i][4]))):
                        conj = False
                # print(conj, inputKata, data[i][0])
                if ('の' in data[i][3] and ('助動詞-ダ' in data[i+1][5] or '助動詞-デス' in data[i+1][5])):
                    conj = True
                    if ('助動詞-ダ' in data[i+1][5]):
                        katadasar = ['ので', 'ノデ']
                    if ('助動詞-デス' in data[i+1][5]):
                        katadasar = ['のです', 'ノデス']
                    # bantuan = 'particle'
            except IndexError as e:
                pass
            
            if ('記号' in data[i][4]):
                conj = False
            # print(conj, inputKata, data[i][0])
            
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
                                if ('助動詞-デス' in data[i][5]):
                                    conj = False
                                    inputKata = True
                    if ('居る' in data[i][3]):
                        if kata:
                            kelompokKataKerja.append("動詞-居る")
                    # fix adjective and adverb combination
                    if ('形状詞' in data[i][4] or '副詞' in data[i][4]):
                        if ('助動詞' in data[i+1][4] or '連体形' in data[i+1][6]):
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
                    # this below will separate verb + もらう but also separat verb + する/くる
                    # or ('動詞' in data[i+1][4] and '非自立' in data[i+1][4])
                    if ('接続助詞' in data[i][4]):
                        if (('非自立' not in data[i+1][4]) ):
                            conj = False
                            inputKata = True
                    
                    # this check if currently have non independent form
                    if ('非自立可能' in data[i][4]):
                        inputKata = True
                        conj = False
                        # check if next iteration have:
                        # 助-動詞/jo-doushi/auxiliary-verb
                        # 非自立/hijiritsu/non-independent form
                        # 接続-助詞/setsuzoku-joshi/conjunctive-particle
                        # if so, keep combining
                        # else, input the word
                        if ('助動詞' in data[i+1][4] or '非自立可能' in data[i+1][4] or '接続助詞' in data[i+1][4]):
                            # kata += data[0]
                            conj = True
                            inputKata = False

                    if ('終助詞' in data[i][4] or '連体形' in data[i][6]):
                        conj = False
                        inputKata = True
                    if (not data[i+1]):
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
                temp = [kata, [], [], [], []]
                if kanji:
                    temp[1] = kanji
                if katadasar:
                    katadasar[1] = self.furigana(katadasar[1], 'hiragana')
                    temp[2] = katadasar
                else:
                    if (combine_count == 1):
                        katadasar = [data[i][3], data[i][2]]
                        katadasar[1] = self.furigana(katadasar[1], 'hiragana')
                        temp[2] = katadasar

                        if ('助詞' in data[i][4]):
                            temp[4] = 'particle'
                        elif ('代名詞' in data[i][4]):
                            temp[4] = 'pronoun'

                if kelompokKataKerja:
                    temp[3] = kelompokKataKerja
                if bantuan:
                    temp[4] = bantuan
                kelompokKata.append(temp)
                kata = ''
                bantuan = ''
                kanji = []
                katadasar = []
                kelompokKataKerja = []
                inputKata = False
                combine_count = 0
        #############END FOR LOOP#####################
        # data/kelompokKata -> kata_parser -> [kata_parser, [kanji, cara baca], [kata_dasar, cara baca], [tipe konjugasi(dapat lebih dari 1)]]
        # pprint(kelompokKata)
        return kelompokKata
    
if (__name__ == "__main__"):
    parse = Parse()
    a = parse.jpParse1("明日はすごく楽しみにしています。しています")
    pprint(a)
    # for x in a:
    #     if x[1]:
    #         print(x[1]) 
