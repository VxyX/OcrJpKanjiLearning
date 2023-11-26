import MeCab
import sqlite3
import sys
import pytesseract
import romkan
from PIL import Image
from pprint import pprint

# to_u = ['ぅ', 'う', 'ぉ', 'お', 'く', 'ぐ', 'こ', 'ご', 'す', 'ず', 'そ', 'ぞ', 'つ', 'づ', 'と', 'ど', 'の', 'ふ', 'ぶ', 'ぷ', 'ほ', 'ぼ', 'ぽ', 'も', 'よ', 'ょ']
# to_i = ['ぇ', 'え', 'け', 'げ', 'せ', 'ぜ', 'て', 'で', 'ね', 'へ', 'べ', 'ぺ' 'め']


class Parse():
    def __init__(self):
        # jp dictionary for MeCab
        self.unidic = r'D:\\Bakup\\Materi\\Semester9\\Skripsi\\program\\orcjplearning\\dic\\unidic'
        self.ipadic = r'D:\\Bakup\\Materi\\Semester9\\Skripsi\\program\\orcjplearning\\dic\\ipadic'

        self.tagger = MeCab.Tagger(f"-d {self.unidic}")
        pass
    
    @staticmethod
    def furigana(text, jenis_huruf='hiragana'or'katakana'or'romaji'):
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
        # text = "こんな風にです。こんなことが"
        # text = "再び、彼は放浪者となって、彼はある日、兄の家にたどり着いた。"
        # text = "こんな、そんな、あんな"
        # text = "アパートの壁が薄いので、隣の部屋の人のいびきまで聞こえてきて、気になって眠れない。"
        # text = "私の両親は、田舎で農業を営んでいる"
        # text = "聞こえる.聞こえない.聞こえます.聞こえません.聞こえた.聞こえなかった.聞こえました.聞こえませんでした.聞こえて.聞こえなくて.聞こえられる.聞こえられない.聞こえさせる.聞こえさせない.聞こえさせられる.聞こえさせられない.聞こえろ.聞こえるな"
        # text = "聞えるんだよ"
        # text = text
        print('Input : ', text, '\n\n')
        result = self.tagger.parse(text) #or parseNBest(n, text)
        # print('Sebelum :\n\n', result, '\n')
        result = result.splitlines() #splitLines untuk pengelompokan tabel berdasarkan kata yang displit MeCab
        # print(result)
        # inisialisasi data untuk menampung hasil MeCab
        data = []
        # pengelompokan berdasarkan tabel output MeCab
        for line in result:
            values = line.split('\t') 
            if (values == ['EOS']):
                continue
            data.append(values)
        print('Sesudah :\n\n', data)
        # exit()
        # inisialisasi sebelum dilakukan parsing
        conj = False
        # dataiter = iter(data)
        next_data_row = None
        words = [] # separated word list
        kelompokKata = [] # 
        kelas_kata = ''
        inputKata = False # checking mixed word/particle
        kata = '' # raw word, can be an inflection of the base word
        katadasar = [] # base word
        kanji = [] # kanji and reading
        combine_count = 0
        skip = False

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
            
            # cek bentuk konjugasi
            if (data[i][5]):
                kelompokKata.append(data[i][5]) # add conj-type
                # 動詞 (youshi) = kata kerja
                # 容詞 (doushi) = kata sifat
                if (("動詞-一般" in data[i][4]) or ("容詞-一般" in data[i][4])
                    or "動詞-非自立可能" in data[i][4]):
                    katadasar = [data[i][3], data[i][2]] #add lexeme/kada dasar
                    # jika katadasar = null, 
                    # input kata awalan merupakan kata dasarnya
            

            # what is this for?
            # if ('サ変可能' in data[i][4]):
            #     # conjVerb = True
            #     try:
            #         if ('非自立可能' in data[i+1][4] or '接尾辞' in data[i+1][4]):
            #             conj = True
            #     except :
            #         pass

            # check and combine verb if: 
            # - 連用形 (renkyoukei/continuous form), 
            # - 連体詞 (rentaishi/pre-noun adjectival/pronomina)
            # - 助詞-準体助詞 ()
            # cek kata dengan konjugasi (renyoukei/連用形) dan (未然形/mizenkei)
            # this fix a problem somehow but i dont know what it is again...
            # i mean, why should i put 助詞-準体助詞?
            # also why use conjugation type like Renyoukei and Meizenkei?
            # if ('連用形' in data[i][6] or '連体詞' in data[i][4] or '助詞-準体助詞' in data[i][4] or '未然形' in data[i][6]):
            #     conj = True
            #     # idk why i write this below...
            #     # may be fix something here but i forgot
            #     try:
            #         if ('連体詞' in data[i][4] and ('名詞-普通名詞-一般' in data[i+1][4] or '名詞' not in data[i+1][4])):
            #             conj = False
            #             pass
            #     except IndexError as e:
            #         pass
            
            if ('連体詞' in data[i][4]):
                conj = True
                # idk why i write this below...
                # may be fix something here but i forgot
                try:
                    if ('連体詞' in data[i][4] and ('名詞-普通名詞-一般' in data[i+1][4] or '名詞' not in data[i+1][4])):
                        conj = False
                        pass
                except IndexError as e:
                    pass
            
            # fix combined phrase with non-independent verb and final-form also not actially verb
            # ex : ある can be verb or pronomina
            # check if theres non independent or suffix in the next iteration
            try:
                # just specific old japanese word
                # still no fix if there's other word like this one
                if ('動詞' in data[i][4] or '容詞' in data[i][4]):
                    if (('接続助詞' in data[i+1][4]) or
                        ('動詞' in data[i+1][4] and ('終止形' or '未然形' in data[i+1][6]))):
                        conj = True
                
                
                if (data[i][3] == 'に' and '文語' in data[i+1][5]):
                    conj = True
                    pass
                    #'助動詞' in data[i+1][4] or 
                if ('助動詞' in data[i+1][4] or '接続助詞' in data[i+1][4]):
                    conj = True
                    inputKata = False
                    if ('名詞' in data[i][4]):
                        
                        katadasar = [data[i][3], data[i][2]]
                
                # this check :
                # 非自立/hijiritsu/non-independent word in next iteration
                # 接尾辞/setsubiji/suffix word in next iteration
                # 助-動詞/jo-doushi/auxalary-verb word in next iteration
                if (('非自立' in data[i+1][4] and not '動詞' in data[i][4]) 
                    or ('接尾辞' in data[i+1][4] and not data[i+1][5]) 
                    or ('助動詞' in data[i+1][5])):
                    conj = True 
                    # prevent combining word if current word is particle
                    # and not particle that attaches to a phrase
                    if (('助詞' in data[i][4] and ('準体助詞' not in data[i][4] and '接続助詞' not in data[i][4]))):
                        conj = False
                print(conj, data[i][0])
                if ('終止形' in data[i][6] and '終助詞' in data[i+1][4]):
                    conj= True
                # if want to separate noun + suru verb enable this below        
                # if ('名詞' in data[i][4]):
                #     conj = False
            except IndexError as e:
                pass
            if ('記号' in data[i][4]):
                conj = False
            # print(conj, inputKata, data[i][0])
            # print(conj)
            
            if conj:
                inputKata = False
                kata += data[i][0]
                try:
                    
                    # i forgor what is this used for...
                    if ('助動詞' in data[i][4]):
                        # kata += data[0]
                        conj = False
                        inputKata = True
                        
                        # fix multiple auxverb and continuous form
                        # this fix 聞えなかった -ta aux verb
                        # but this create a problem for -desu aux verb
                        if ('助動詞' in data[i+1][4] or '接続助詞' in data[i+1][4] or '終助詞' in data[i+1][4]):
                            conj = True
                            inputKata = False
                            # print(inputKata, data[i][0])
                            if ('助動詞-デス' in data[i+1][5]):
                                conj = False
                                inputKata = True
                                # print(inputKata, data[i][0])
                                if ('助動詞-マス' in data[i-1][5]):
                                    conj = True
                                    inputKata = False
                                    # print(inputKata, data[i][0])
                    
                    ############ print(conj, data[i][0])
                    # fix adjective and adverb combination
                    # i also forgor about this... 
                    if ('形状詞' in data[i][4] or '副詞' in data[i][4]):
                        if ('助動詞' in data[i+1][4]):
                            conj = True
                            inputKata = False
                        else :
                            conj = False
                            inputKata = True
                    
                    # keep putting this here just in case theres another problem
                    # fix noun suffix 者 (orang) 
                    # -> 冒険者 (Petualang) 
                    # -> 医者 (Dokter)
                    # if (('接尾辞' in data[i][4] and 'サ変可能' in data[i-1][4])):
                    #     inputKata = True
                    #     conj = False

                    # this fix suffix that change adjective word to noun
                    # ex: 優しさ: 
                    # 優し/yasashi/baik -> adjective/kata sifat
                    # 優しさ/yasashisa/kebaikan-> さ suffix -> kata benda
                    # apparently this also fix 者 suffix... maybe...
                    if ('接尾辞' in data[i][4] and '名詞的' in data[i][4]):
                        inputKata = True
                        conj = False
                        k_temp = ''
                        if '名詞的' in data[i][4]:
                            if k_temp:
                                k_temp += '-'
                            k_temp += '名詞的'
                        if '接尾辞' in data[i][4]:
                            if k_temp:
                                k_temp += '-'
                            k_temp += '接尾辞'+data[i][3]
                        if k_temp:
                            # kelompokKataKerja.append(k_temp)
                            pass
                    
                    # fix 接続/setsuzoku/conjuctive 助詞/joshi/particle -Te that has 非自立/hijiritsu/non-independent/ form on the next iteration
                    # ex : 聞こえてきて [kikoe(verb -> base = 聞く) -te(particle) -ki(non-independent) -te(particle)]
                    #
                    #  this check the first -Te particle
                    if ('接続助詞' in data[i][4]):
                        # if there's no 'non-independent' form in next iteration, then input the word
                        # else, continue combining
                        if ('非自立' not in data[i+1][4]):
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
                    
                    
                    # this check if current iteration is 終-助詞/shuu-joshi/final-particle
                    if ('終助詞' in data[i][4]):
                        conj = False
                        inputKata = True
                    
                except IndexError as e:
                    inputKata = True
                # if next_data_row:
                #     if ('終止形' in next_data_row[6]):
                #         conj = False
                #         inputKata = True
                #     kata += next_data_row[0]
                #     next_data_row = None
            else :
                inputKata = True
                kata += data[i][0]
            
            # print(conjVerb, inputkata, kata)
            if inputKata:
                # [inputKatam, [kanji, reading], [kata_dasar], [kelompok_kata], [bantuan...]]
                temp = [kata, [], [], [], []]
                if kanji:
                    temp[1] = kanji
                if katadasar:
                    katadasar[1] = self.furigana(katadasar[1], 'hiragana')
                    temp[2] = katadasar
                else:
                    
                    if (combine_count == 1):
                        temp[2] = [data[i][3], data[i][2]]
                        if ('助詞' in data[i][4]):
                            temp[4] = 'particle'
                        elif ('代名詞' in data[i][4]):
                            temp[4] = 'pronoun'
                if kelompokKata:
                    temp[3] = kelompokKata
                words.append(temp)
                kata = ''
                kanji = []
                katadasar = []
                kelompokKata = []
                combine_count = 0
            # conj = False
            # inputKata = True
        #############END FOR LOOP#####################
        # data/kelompokKata -> kata_parser -> [kata_parser, [kanji, cara baca], [kata_dasar, cara baca], [tipe konjugasi(dapat lebih dari 1)]]
        # pprint(kelompokKata)
        return words

# auxverb = 助動詞 / jodoushi
# list -> -マス, -ヌ, -デス
# auxverb masu + nu = formal negative
# auxverb desu = to be / is
# auxverb desu + nu = to be / is negative
# combine all = formal negative + tobe / is
# noun + サ行変格 (する) -> verb

if (__name__ == "__main__"):
    parse = Parse()
    #聞こえる.聞こえない.聞こえます.聞こえません.聞こえた.聞こえなかった.聞こえました.聞こえませんでした.聞こえて.聞こえなくて.聞こえられる.聞こえられない.聞こえさせる.聞こえさせない.聞こえさせられる.聞こえさせられない.聞こえろ.聞こえるな
    a = parse.jpParse1("そのつもりだったんですが")
    print('\n')
    # print(romkan.to_roma('遊ぶ'))
    pprint(a)
    # for x in a:
    #     if x[1]:
    #         print(x[1]) 
