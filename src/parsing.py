import MeCab
from pprint import pprint
import romkan
import os
import re


class Parse():
    def __init__(self):
        # jp dictionary for MeCab
        filepath = os.path.abspath(os.path.dirname(__file__))
        self.unidic = os.path.join(os.path.dirname(filepath), 'dic', 'unidic').replace('\\','\\\\')
        self.ipadic = os.path.join(os.path.dirname(filepath), 'dic', 'ipadic').replace('\\','\\\\')

        self.tagger = MeCab.Tagger(f"-d {self.unidic}")
        pass
    
    @staticmethod
    def convKanaRo(text, jenis_huruf='hiragana'or'katakana'or'romaji'):
        txt = text
        new_txt = ''
        if jenis_huruf == 'romaji':
            new_txt = romkan.to_roma(text)
        else:
            for char in txt:
                char_code = ord(char)
                if jenis_huruf == 'hiragana':
                    if char == 'ー':
                        new_txt += 'ー'
                        continue
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
                    if char == 'ー':
                        new_txt += 'ー'
                        continue
                    if not 0x30A0 <= char_code <= 0x30FF:
                        if 0x3040 <= char_code <= 0x309F:
                            # Kode hiragana adalah kode katakana - 96
                            katakana_code = char_code + 96 
                            katakana_character = chr(katakana_code)
                            new_txt += katakana_character
            

        return new_txt

    def furigana(self, wordWithKanji, reading) -> list:
        kanjilist = list(wordWithKanji)
        kanjilist2 = list(wordWithKanji)
        hiraganalist = list(reading)
        hiraganalist2= list(reading)
        new_hiList = []
        new_kList = []
        last_kanji = False
        if hiraganalist:
            for index, c in enumerate(kanjilist):
                c_code = ord(c)
                # print(c , c_code)
                if (not (0x3040 <= c_code <= 0x309F) and not (0x30A0 <= c_code <= 0x30FF)):
                    if last_kanji:
                        new_kList[-1] += c
                    else:
                        new_kList.append(c)
                        last_kanji = True
                   
                else:
                    # combine kanji if theres multiple kanji in a row
                    if (last_kanji):
                        # print(c, hiraganalist)
                        for index1, c1 in enumerate(hiraganalist):
                        # print(c, c1, kanjilist)
                        # check if reading and word have the same char
                            if (c == c1):
                                # check if 
                                if (index1 != 0):
                                    str_hi = ''
                                    for h in range(index1):
                                        str_hi += hiraganalist[h]
                                    new_hiList.append(str_hi)
                                else:
                                    continue
                                # this will remove the current word and earlier index
                                # to prevent checking the same character
                                hiraganalist = hiraganalist[index1+1:]
                                kanjilist2.pop(0)
                                # print(hiraganalist)
                                break
                        last_kanji = False
                    else:
                        kanjilist2.pop(0)
                        hiraganalist.pop(0)
                if(index == len(kanjilist) - 1):
                    if (hiraganalist):
                        str_hi = ''.join(hiraganalist)
                        new_hiList.append(str_hi)
        return [new_kList, new_hiList]
                                

    def segmentasiTeks(self, text, debug=False):
        # print()
        # print('input text :', text)
        result = self.tagger.parse(text)
        # print()
        # print('output MeCab (raw):')
        # print(result)
        # return
        result = result.splitlines() 

       
        data = []
        for line in result:
            values = line.split('\t') 
            if (values == ['EOS']):
                continue
            data.append(values)
        # print()
        # print('output MeCab (array):')
        # pprint(data)
        # print()
        # return
        if debug:
            pprint(data)
        

        # inisialisasi sebelum dilakukan parsing
        conj = False
        kelompokKata = [] # list semua kata
        tipeKonjugasi = [] # list tipe konjugasi (kelompok kata kerja)
        bentukKonjugasi = [] # list bentuk konjugasi (renyoukei, meireikei, dll)
        inputKata = False
        kata = ''
        katadasar = []
        temp_katadasar = []
        bantuan = ''
        kanji = []
        combine_count = 0
        prenoun = False
        combine_katadasar = False
        pattern2 = re.compile("[0-9]+|[a-zA-Z]+\'*[a-z]*")
        #############awal looping parser##############
        for i in range(len(data)):
            # pattern3 = pattern2.findall(data[i][0])
            # if ('記号' in data[i][4] or pattern3):
            #     conj = False
            #     combine_katadasar = False
            #     inputKata = True
            #     kata += data[i][0]
            #     if not katadasar:
            #         katadasar = [data[i][3], data[i][2]]
            #     continue
            # combine_count += 1
            
            
            # if skip:
            #     skip = False
            #     continue

            ########## cek apakah terdapat kanji ############
            kanji_check = data[i][0]
            kanjilist = list(kanji_check)
            kanjilist2 = list(kanji_check)
            kanalist = list(data[i][1])
            hiraganalist = [] # will replace the katakana reading to hiragana
            temp_count = 0
            last_kanji = False
            ada_kanji = False
            new_hiList = []
            new_kList = []
            for x in range(len(kanalist)):
                
                c = kanalist[x]
                if (c == 'ー'):
                    # mengubah pelafalan vokal panjang menjadi huruf yang sesuai
                    if hiraganalist:
                        c_index = x - 1
                        tes = self.convKanaRo(hiraganalist[c_index], 'romaji')
                        if debug:
                            print(tes)
                        if tes[-1] == 'i' or tes[-1] == 'e':
                            c = 'イ'
                            # check if 2 letter are the same vocal
                            #ex : ii, ee, oo, uu
                            # otherwise, ii, ei, ou, uu
                            # print()
                            if tes[-1] == self.convKanaRo(data[i][2][c_index+1], 'romaji'):
                                c = data[i][2][c_index+1]
                        if tes[-1] == 'u' or tes[-1] == 'o':
                            c = 'ウ'
                            try:
                                if tes[-1] == self.convKanaRo(data[i][2][c_index+1], 'romaji'):
                                    c = data[i][2][c_index+1]
                            except Exception as e:
                                if '意志推量形' in data[i][6]:
                                    c = 'ウ'
                                    pass
                        # try:
                        #     c_index = kanalist.index(c)
                        #     c = data[i][2][c_index]
                        # except IndexError as e:
                        #     try:
                        #         c_index = data[i][0].index(hiraganalist[-1])
                        #         c = data[i][0][c_index+1]
                        #     except:
                        #         pass
                hiraganalist.append(self.convKanaRo(c, 'hiragana'))

            if debug:
                print(hiraganalist)
                
            for x in range(len(kanji_check)):
                kanjiCode = ord(kanji_check[x])
                if kanjiCode > 0x4e00 and kanjiCode <= 0x9fff:
                    ada_kanji = True
            if data[i][3] == '転生':
                kanji = [data[i][3], self.convKanaRo(data[i][2], 'hiragana')]
                ada_kanji = False
            if ada_kanji:
                for indexK, c in enumerate(kanjilist):
                    
                    # idk why mecab use てんしょー for pronoun and てんせい for base word...
                    # for better conversion, i should make manual dictionary for u and o pronoun...
                    # but this is "okay" for now
                    
                    kanjiCode = ord(c)
                    if kanjiCode > 0x4e00 and kanjiCode <= 0x9fff:
                        pass
                    if (not (0x3040 <= kanjiCode <= 0x309F) and not (0x30A0 <= kanjiCode <= 0x30FF)):
                        # gabungin jika 2 kanji berurutan
                        if last_kanji:
                            new_kList[-1] += c
                        else:
                            new_kList.append(c)
                            last_kanji = True
                    
                    else:
                        # combine kanji if theres multiple kanji in a row
                        if (last_kanji):

                            if debug:
                                print(c, hiraganalist)

                            for index1, c1 in enumerate(hiraganalist):
                            # print(c, c1, kanjilist)
                            # check if reading and word have the same char
                                if (c == c1):
                                    # check if 
                                    if (index1 != 0):
                                        str_hi = ''
                                        for h in range(index1):
                                            str_hi += hiraganalist[h]
                                        new_hiList.append(str_hi)
                                    else:
                                        continue
                                    # this will remove the current word and earlier index
                                    # to prevent checking the same character
                                    hiraganalist = hiraganalist[index1+1:]
                                    kanjilist2.pop(0)
                                    # print(hiraganalist)
                                    break
                            last_kanji = False
                        else:
                            kanjilist2.pop(0)
                            hiraganalist.pop(0)
                if(indexK == len(kanjilist) - 1):
                    if (hiraganalist):
                        str_hi = ''.join(hiraganalist)
                        new_hiList.append(str_hi)
                if (kanji):
                    kanji[0].extend(new_kList)
                    kanji[1].extend(new_hiList)
                else :
                    temp = [new_kList, new_hiList]
                    kanji += temp
                ada_kanji = False
            ########## cek apakah terdapat kanji ############
            
            if not katadasar:
                katadasar = [data[i][3], data[i][2]]
            
                
            if conj:
                if '連体詞' in data[i-1][4]:
                    prenoun = True
                if prenoun:
                    if '連用形-ニ' in data[i][6]:
                        katadasar[0] += data[i][0]
                        katadasar[1] += data[i][1]
                    else:
                        katadasar[0] += data[i][3]
                        katadasar[1] += data[i][2]
                if '連体形' in data[i][4]:
                    pass
            
            if (data[i][6]):
                if data[i][6] in bentukKonjugasi:
                    pass
                else:
                    bentukKonjugasi.append(data[i][6])

            # cek tipe kelompok kata kerja
            if (data[i][5]):
                tipeKonjugasi.append(data[i][5])
                # 動詞 (youshi) = kata kerja
                # 容詞 (doushi) = kata sifat
                if ((("動詞-一般" in data[i][4]) 
                    or ("容詞-一般" in data[i][4]) 
                    or ("動詞-非自立可能" in data[i][4])) 
                    and not ('連体形' in data[i][6])):
                    if not katadasar:
                        katadasar = [data[i][3], data[i][2]]

                        # handle some common word
                        if ('存ずる' in data[i][3]):
                            katadasar = ['存じる', 'ゾンジル']
            

            # if ('サ変可能' in data[i][4]):
            #     # conjVerb = True
            #     try:
            #         if ('非自立可能' in data[i+1][4] or '接尾辞' in data[i+1][4]):
            #             conj = True
            #     except :
            #         pass

            
            # print(conj, inputKata, data[i][0])
            # fix combined phrase with non-independent verb and final-form also not actially verb
            # ex : ある can be verb or pronomina
            try:
                # combine verb 連用形 (renkyoukei/continuous form), 連体詞 (rentaishi/pre-noun adjectival/pronomina)
                # 助詞-準体助詞 ()?
                # if ('融合' in data[i][6]):
                #     conj = True
                # print(conj, inputKata, data[i][0])
                if ('連用形' in data[i][6]  
                    or '未然形' in data[i][6]):
                    conj = True
                    try:
                        if (('形容詞' in data[i][4] and ('名詞' in data[i+1][4] or '形容詞' in data[i+1][4] or '動詞' in data[i+1][4])) or
                            ('接続助詞' not in data[i+1][4] and not data[i+1][6])):
                            conj = False
                            # print(data[i][0])
                        if ('五段' in data[i+1][5]):
                            conj = False
                            if ('ちゃう' in data[i+1][3]):
                                conj = True
                    except Exception as e:
                        pass
                    
                # print(conj)
                # what is this for????
                # try:
                #     if ('連体詞' in data[i][4]):
                #         conj = True
                #         if (('連体詞' in data[i][4] and  ('名詞' in data[i+1][4]))):
                #             conj = False
                # except Exception as e:
                #         pass
                if debug:
                    print(conj)
                # print(conj, inputKata, data[i][0])
                if ('動詞' in data[i][4] 
                    or '容詞' in data[i][4] 
                    or '副詞' in data[i][4]):
                    try:
                        if (('接続助詞' in data[i+1][4]) or
                            ('動詞' in data[i+1][4] and ('終止形' in data[i+1][6] or '未然形' in data[i+1][6] or '連体形' in data[i+1][6]))):
                            conj = True
                            if ('五段' in data[i+1][5]):
                                conj = False
                                if ('ちゃう' in data[i+1][3]):
                                    conj = True
                            if (('動詞' in data[i][4] and not '助動詞' in data[i][4]) and '動詞' in data[i+1][4] and not '助動詞' in data[i+1][4]):
                                conj = False
                            pass
                    except Exception as e:
                        pass
                        
                if debug:
                    print(conj)
                # print(conj, inputKata, data[i][0])
                try:
                    if ('非自立' in data[i+1][4]):
                        conj = True 
                        try:
                            if ('格助詞' in data[i][4] or '動詞' in data[i+1][4]):
                                conj = False
                                if ('接続助詞' in data[i][4]):
                                    conj = True
                        except Exception as e:
                            pass
                except Exception as e:
                        pass
                if debug:
                    print(conj)
                # print(conj, inputKata, data[i][0])
                try:
                    if (data[i][3] == 'に' and '文語' in data[i+1][5]):
                        conj = True
                except Exception as e:
                        pass
                if debug:
                    print(conj)
                # print(conj, inputKata, data[i][0])
                # This below combine suffix like -sama, or -sha...
                # '接尾辞' in data[i+1][4] or 
                # but i think its better to separate them and search for specific suffix on jisho
                try:
                    if (('非自立' in data[i+1][4] and not ('動詞' in data[i][4] or '形容詞' in data[i][4])) 
                        or ((('接続助詞' in data[i+1][4]) and not data[i+1][5]))):
                        conj = True 
                        combine_katadasar = True
                        
                        # if '終止形' in data[i+1][6] or '連体形' in data[i+1][6]:
                        #     conj = False
                        #     combine_katadasar = False
                        
                        if ('力' in data[i+1][3]):
                            conj = False
                            combine_katadasar = False
                        # print(conj, combine_katadasar)
                        # prevent combining word if current word is particle
                        # and not particle that attaches to a phrase
                        # and '接続助詞' not in data[i][4]) -> fix combined oresama
                        # apparently joshi and jodoushi are the same in python...
                        if (('助詞' in data[i][4])):
                            if ('助詞' in data[i][4] and ('準体助詞' not in data[i][4] and '接続助詞' not in data[i][4])):
                                conj = False
                                combine_katadasar = False
                            # print(data[i][4])
                        # print(conj, combine_katadasar)
                        # pisahin kata dasar noun + suru
                        if ('名詞' in data[i][4] and 'サ行変格' in data[i+1][5]):
                            conj = True
                            combine_katadasar = False
                        # print(conj, combine_katadasar)
                except Exception as e:
                        pass
                if debug:
                    print(conj, combine_katadasar)
                if '接頭辞' in data[i-1][4]:
                    if '兄' in data[i][3]:
                        kanji[1][0] = 'にい'
                        katadasar[0] = '兄'
                        katadasar[1] = 'にい'
                    if '姉' in data[i][3]:
                        kanji[1][0] = 'ねえ'
                        katadasar[1] = '姉'
                        katadasar[1] = 'ねえ'
                    
                    kata = kelompokKata[-1][0] + kata
                    if kelompokKata[-1][1]:
                        # need improve later, current only 1 kanji
                        # have to handle multiple kanji
                        kanji[0] = kelompokKata[-1][1][0] + kanji[0]
                        kanji[1] = kelompokKata[-1][1][1] + kanji[1]
                    if kelompokKata[-1][3]:
                        tipeKonjugasi.append(kelompokKata[-1][3][0])
                    if kelompokKata[-1][4]:
                        bentukKonjugasi.append(kelompokKata[-1][4][0])
                    kelompokKata.pop()

                if '代名詞' in data[i][4]:
                    try:
                        if '係助詞' in data[i+1][4] or '副助詞' in data[i+1][4]:
                            conj = True
                    except Exception as e:
                        pass
                
                if debug:
                    print(conj)
                    
                # print(conj, inputKata, data[i][0])
                
                # fixing separation on particle
                # 意志推量形 fix darou & deshou
                # thiss below, all of them are custom(manual) fix...
                try:
                    if ('の' in data[i][3] 
                        and (('助動詞-ダ' in data[i+1][5] and '意志推量形' not in data[i+1][6]) 
                            or ('助動詞-デス' in data[i+1][5] and '意志推量形' not in data[i+1][6]))):
                        conj = True
                        if katadasar[0] == data[i][3]:
                            if ('助動詞-ダ' in data[i+1][5]) and ('連用形' in data[i+1][6]):
                                katadasar = ['ので', 'ノデ']
                            if ('助動詞-ダ' in data[i+1][5]) and ('終止形' in data[i+1][6]):
                                katadasar = ['のだ', 'ノダ']
                            if ('助動詞-デス' in data[i+1][5]):
                                katadasar = ['のです', 'ノデス']
                        if 'なら' in data[i+1][0] and '助動詞-ダ' in data[i+1][5]:
                            
                            conj = False
                        try:
                            if 'から' in data[i+2][3]:
                                conj = False
                                katadasar = []
                        except Exception as e:
                            pass
                except Exception as e:
                        pass
                try:
                    if ('誰' in data[i][3] and 'で' in data[i+1][3] and 'も' in data[i+2][3]):
                        conj = True
                        katadasar = ['誰でも', 'だれでも']
                except Exception as e:
                    pass
                if ('で' in data[i][3]):
                    try:
                        if ('も' in data[i+1][3]):
                            if not conj:
                                conj = True
                                katadasar = ['でも', 'でも']
                    except Exception as e:
                        pass
                try:
                    if ('じゃ' in data[i][0] and 'だ' in data[i][3]) and ('無い' in data[i+1][3]):
                        katadasar = ['じゃない','じゃない']
                        # bantuan = 'particle'
                except Exception as e:
                        pass
                if ('だ' in data[i][3] and '仮定形' in data[i][6]):
                    katadasar = ['なら','なら']
                # pronoun + da aux
                try:
                    if ('何' in data[i][3] and ('助動詞-ダ' in data[i+1][5] and not 'な' in data[i+1][0])):
                        combine_katadasar = True
                        conj = True
                except Exception as e:
                        pass
                try:
                    if ('な' in data[i][0] and 'ん' in data[i+1][0] and 'だ' in data[i+2][0]):
                        conj = True
                        combine_katadasar = True
                except Exception as e:
                    pass
                try:
                    if ('少ない' in data[i][3] and 'とも' in data[i+1][3] and '接続助詞' in data[i+1][4]):
                        conj = True
                        combine_katadasar = True
                except Exception as e:
                        pass
                try:
                    if '掛かる' in data[i][3] and 'て' in data[i+1][3] and '命令形' in data[i+2][6]:
                        conj = True
                        combine_katadasar = True
                except Exception as e:
                    pass

                ##kamus manual
                try:
                    if '萌える' in data[i][3] and ((data[i+1][4] != '助動詞' or  'デス' in data[i+1][5]) and not ('接続助詞' in data[i+1][4])):
                        
                        conj = False
                        combine_katadasar = False
                        katadasar = ['萌え', 'もえ']
                except Exception as e:
                    pass

                if '推し' == data[i][0]:
                    katadasar = ['推し', 'おし']
                if '代名詞' in data[i][4] and 'てまえ' in data[i][3]:
                    conj = False
                    combine_katadasar = False
                    katadasar = ['てめえ','てめえ']

                try:
                    if '下さる' in data[i+1][3]:
                        combine_katadasar = False
                except Exception as e:
                        pass
            except IndexError as e:
                pass

            pattern3 = pattern2.findall(data[i][0])
            if ('記号' in data[i][4] or pattern3):
                conj = False
                combine_katadasar = False
                if '記号' in data[i][4]:
                    bantuan = 'symbol'
            if debug:
                print(conj, inputKata, combine_katadasar, kata, data[i][0])
                print(temp_katadasar)
            
            if conj:
                if combine_katadasar:
                    if temp_katadasar:
                        if kata != temp_katadasar[0]:
                            combine_katadasar = False
                    else:
                        if kata:
                            combine_katadasar = False
                if combine_katadasar:
                    if '接頭辞' in data[i-1][4]:
                        if data[i-1][0] in kata:
                            # print(kata)
                            temp_katadasar=[data[i-1][0], data[i-1][1]]
                    
                    readlist = []
                    # if not temp_katadasar:
                    #     temp_h = data[i-1][1]+data[i][1]
                    #     temp_h2 = data[i-1][1]+data[i][1]
                    #     temp_k = data[i-1][0]+data[i-1][0]
                    # else:
                    # problem -> ['お兄ちゃん', 'おあにちゃん']
                    temp_h = data[i][1]
                    temp_h2 = data[i][1]
                    temp_k = data[i][0]
                    kanalist = list(temp_h)
                    for c in range(len(temp_h)):
                        c = temp_h2[c]
                        if c == "ー":
                            c_index = kanalist.index(c) - 1
                            tes = self.convKanaRo(temp_h2[c_index], 'romaji')
                            if tes[-1] == 'i' or tes[-1] == 'e':
                                c = 'い'
                                if tes[-1] == self.convKanaRo(data[i][2][c_index+1], 'romaji'):
                                        c = data[i][2][c_index+1]
                                readlist.append(c)
                            if tes[-1] == 'u' or tes[-1] == 'o':
                                c = 'う'
                                if tes[-1] == self.convKanaRo(data[i][2][c_index+1], 'romaji'):
                                        c = data[i][2][c_index+1]
                                readlist.append(c)
                                
                            # try:
                            #     c_index = kanalist.index(c)
                            #     c = temp_h2[c_index]
                            #     readlist.append(c)
                            # except IndexError as e:
                            #     try:
                            #         c_index = temp_k.index(readlist[-1])
                            #         c = temp_k[c_index+1]
                            #         readlist.append(c)
                            #     except:
                            #         pass
                        else:
                            readlist.append(c)
                            pass
                    # print(readlist)
                    if not temp_katadasar:
                        # temp_katadasar = [data[i-1][0] + temp_k, data[i-1][1] + ''.join(readlist)]
                        temp_katadasar = [temp_k, ''.join(readlist)]
                    else:
                        temp_katadasar[0] += data[i][0]
                        temp_katadasar[1] += ''.join(readlist)
                    if debug:
                        print(temp_katadasar)
                
                inputKata = False
                kata += data[i][0]
                if (not katadasar and
                    ('名詞' in data[i][4] or '動詞' in data[i][4] or '形容詞' in data[i][4]) 
                    and ('助動詞' not in data[i][4] and '融合' not in data[i-1][6])):
                    
                    katadasar = [data[i][3], data[i][2]]
                    # if ('者' in data[i+1][3]):
                    #     katadasar[0] += '者'
                    #     katadasar[1] += 'シャ'
                try:
                    if ('記号' in data[i+1][4]):
                        conj = False
                        inputkata = True
                    #below problem :
                    #-tai form/ desire form (verb + tai/takunai/takatta/takunakatta)
                    if ('助動詞' in data[i][4]):
                        # kata += data[0]
                        conj = False
                        inputKata = True
                        # fix multiple auxverb and continuous form
                        if ('助動詞' in data[i+1][4] or '接続助詞' in data[i+1][4] or '融合' in data[i][6]):
                                conj = True
                                inputKata = False
                                if ('助動詞-デス' in data[i][5] and not '助動詞' in data[i+1][4]):
                                    conj = False
                                    inputKata = True
                        if ('助動詞-タイ' in data[i][5] and '連用形' in data[i][6]):
                            conj = True
                            inputKata = False
                        
                    # print(conj, inputKata, data[i][0])
                    # conjugation List already in mecab
                    # jodoushi :
                    # 助動詞-ナイ
                    # 助動詞-レル
                    # 助動詞-デス
                    # 
                    if debug:
                        print(data[i][3])
                    if ('居る' in data[i][3]):
                        if kata != data[i][0]:
                            tipeKonjugasi.append("conj-いる")                   
                    if ('てる' in data[i][3]):
                        if kata != data[i][0]:
                            tipeKonjugasi.append("conj-てる")
                    if ('て' in data[i][3] and '助詞' in data[i][4]):
                        
                        if kata != data[i][0]:
                            tipeKonjugasi.append("conj-て")
                    if ('ちゃう' in data[i][3]):
                        if kata != data[i][0]:
                            tipeKonjugasi.append("conj-ちゃう")
                    if ('せる' in data[i][3]):
                        if ('せる' == data[i][3]) or ('させる' == data[i][3]):
                            if kata != data[i][0]:
                                tipeKonjugasi.append("助動詞-セル")
                    if ('呉れる' in data[i][3]):
                        if kata != data[i][0]:
                            tipeKonjugasi.append("conj-くれる")
                    # if ('ます' in data[i][3]):
                    #     if len(kata) > len(data[i][0]):
                    #         kelompokKataKerja.append("conj-いる")


                            # kelompokKataKerja.append("動詞-いる")
                    # fix adjective and adverb combination
                    # print(conj, inputKata, data[i][0])
                    if ('形状詞' in data[i][4] or '副詞' in data[i][4]):
                        if ('助動詞' in data[i+1][4] or '連体形' in data[i+1][6]):
                            conj = True
                            inputKata = False
                        else :
                            conj = False
                            inputKata = True
                    # print(conj, inputKata, data[i][0])
                    # 接尾辞 = suffix = setsubiji
                    # fix noun suffix like 者 (orang) -> 冒険者 (Petualang) 医者 (Dokter)
                    # サ変可能 fix for noun like 冒険 (berpetualang)
                    # 代名詞 fix for pronoun like 俺 + 様
                    if ('接尾辞' in data[i][4] and ('サ変可能' in data[i-1][4] or '代名詞' in data[i-1][4] or '格助詞' in data[i+1][4])):
                        inputKata = True
                        conj = False
                        k_temp = ''
                        k_temp += '接尾辞'+'-'+data[i][3]
                        tipeKonjugasi.append(k_temp)
                    # print(conj, inputKata, data[i][0])
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
                            # if 'なら' in data[i+1][0] and 'だ' in data[i+1][3]:
                            if '終止形' in data[i][6]:
                                inputKata = True
                                conj = False
                    # special case particle
                    if(kata == 'でも'):
                        inputKata = True
                        conj = False

                    if '係助詞' in data[i][4] or '副助詞' in data[i][4]:
                        if '代名詞' in data[i-1][4]:
                            conj = False
                            inputKata = True

                    if ('終助詞' in data[i][4] or '連体形' in data[i][6]):
                        conj = False
                        inputKata = True
                        try:
                            if ('な' in data[i][0] and 'ん' in data[i+1][0] and 'だ' in data[i+2][0]):
                                conj = True
                                inputKata = False
                        except Exception as e:
                            pass
                            # trash parser why tf they put jodoushi-da on na?
                            # why they separat na and n??? its supposed to be
                            # nan and da wtfuck
                    
                    if ('来る' in data[i][3]):
                        conj = False
                        inputKata = True

                    if '下さる' in data[i+1][3]:
                        conj = False
                        inputKata = True
                    if '遣る' in data[i+1][3]:
                        conj = False
                        inputKata = True
                    if '貰う' in data[i+1][3]:
                        conj = False
                        inputKata = True
                    if 'から' in data[i+1][3] and not ('だ' in data[i][3]):
                        conj = False
                        inputKata = True
                    if 'デス' in data[i+1][5]:
                        conj = False
                        inputKata = True
                    

                    if ('記号' in data[i+1][4]):
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
                temp = [kata, [], [], [], [], []]
                if kanji:
                    if '私' in kanji[0]:
                        kanji = [['私'], ['わたし']]
                    temp[1] = kanji
                
                if katadasar:
                    # if '接尾辞' in data[i][4] and not ((data[i][0] in katadasar[0]) or (data[i][3] in katadasar[0])):
                    #     katadasar[0] += data[i][0]
                    #     katadasar[1] += data[i][1] 
                    # print()
                    # print(katadasar)
                    # print()
                    if '私' in katadasar[0]:
                        katadasar = ['私', 'わたし']
                    if '-' in katadasar[0]:
                        c_index = katadasar[0].index('-')
                        katadasar[0] = katadasar[0][:c_index]
                    if combine_katadasar:
                        # print(kata)
                        if temp_katadasar:
                            katadasar = temp_katadasar
                        # temp_kata = katadasar[0]
                        # katadasar[0] = kata
                        # if temp[1] and kata.replace(temp_kata, '') in temp[1][0]:
                        #     kanji_index = temp[1][0].index(kata.replace(temp_kata, ''))
                        #     katadasar[1] = katadasar[1] + temp[1][1][kanji_index] +
                        # katadasar[1] = katadasar[1] + kata.replace(temp_kata, '')
                    katadasar[1] = self.convKanaRo(katadasar[1], 'hiragana')
                    temp[2] = katadasar

                else:
                    # print(kata)
                    if (combine_count == 1):
                        katadasar = [data[i][3], data[i][2]]
                        katadasar[1] = self.convKanaRo(katadasar[1], 'hiragana')
                        temp[2] = katadasar
                        # print(katadasar)
                        if ('意志推量形' in data[i][6]):
                            katadasar = [data[i][0], data[i][1]]
                            katadasar[1] = self.convKanaRo(katadasar[1], 'hiragana')
                            temp[2] = katadasar
                        if '記号' in data[i][4]:
                            temp[2] = []
                            temp[5] = 'symbol'
                        if ('助詞' in data[i][4]):
                            temp[5] = 'particle'
                        elif ('代名詞' in data[i][4]):
                            temp[5] = 'pronoun'

                if tipeKonjugasi:
                    temp[3] = tipeKonjugasi
                if bentukKonjugasi:
                    temp[4] = bentukKonjugasi
                if bantuan:
                    temp[5] = bantuan
                kelompokKata.append(temp)
                kata = ''
                bantuan = ''
                kanji = []
                combine_katadasar = False
                katadasar = []
                temp_katadasar = []
                tipeKonjugasi = []
                bentukKonjugasi = []
                inputKata = False
                combine_count = 0
                prenoun = False
        #############END FOR LOOP#####################
        # data/kelompokKata -> kata_parser -> [kata_parser, [kanji, cara baca], [kata_dasar, cara baca], [tipe konjugasi(dapat lebih dari 1)]]
        # pprint(kelompokKata)
        return kelompokKata
    
    def segmentasiTeksTest(self, text):
        # text = "聞こえる.聞こえない.聞こえます.聞こえません.聞こえた.聞こえなかった.聞こえました.聞こえませんでした.聞こえて.聞こえなくて.聞こえられる.聞こえられない.聞こえさせる.聞こえさせない.聞こえさせられる.聞こえさせられない.聞こえろ.聞こえるな"
        # text = "切る.切らない.切ります.切った.切って.切られる.切れる.切らせる.切れば.切れ.切ろう"
        # text = "食べる.食べない.食べます.食べません.食べた.食べなかった.食べました.食べませんでした.食べて.食べなくて.食べられる.食べられない.食べさせる.食べさせない.食べさせられる.食べさせられない.食べろ.食べるな"
        result = self.tagger.parse(text) #or parseNBest(n, text)
        # print('Output : \n')
        result = result.splitlines() #splitLines untuk pengelompokan tabel berdasarkan kata yang displit MeCab

        # inisialisasi data untuk menampung hasil MeCab
        data = []
        # pengelompokan berdasarkan tabel output MeCab
        for line in result:
            values = line.split('\t') 
            if (values == ['EOS']):
                continue
            data.append(values)
        pprint(data)
        tester = ''
        for d in range(len(data)):
            tester += data[d][0] + ' '
        print()

        # inisialisasi sebelum dilakukan parsing
        conj = False
        kelompokKata = []
        kelompokKataKerja = []
        inputKata = False
        kata = ''
        katadasar = []
        bantuan = ''
        kanji = []
        skip = False
        combine_count = 0
        prenoun = False

        for i in range(len(data)):
            combine_count += 1
            # if skip:
            #     skip = False
            #     continue

            ########## cek apakah terdapat kanji ############
            kanji_check = data[i][0]
            kanjilist = list(kanji_check)
            for char in kanjilist:
                # idk why mecab use てんしょー for pronoun and てんせい for base word...
                # for better conversion, i should make manual dictionary for u and o pronoun...
                # but this is "okay" for now
                if data[i][3] == '転生':
                    kanji = [data[i][3], self.convKanaRo(data[i][2])]
                    break
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
                                    try:
                                        c_index = data[i][0].index(hiraganalist[-1])
                                        c = data[i][0][c_index+1]
                                    except:
                                        pass
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
                    last_kanji = False
                    if hiraganalist:
                        for index, c in enumerate(kanjilist):
                            c_code = ord(c)
                            # print(c , c_code)
                            if (0x3040 <= c_code <= 0x309F):
                                last_kanji = False
                                # print(c , c_code)
                                for c1 in hiraganalist:
                                    # check if reading and word have the same char
                                    if (c == c1):
                                        # check if 
                                        h_index = hiraganalist.index(c1)
                                        # print(h_index)
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
                                # combine kanji if theres multiple kanji in a row
                                if (last_kanji):
                                    temp = new_kList[-1]
                                    temp += c
                                    new_kList[-1] = temp
                                else:
                                    new_kList.append(c)
                                    last_kanji = True
                                if(index == len(kanjilist) - 1):
                                    if (hiraganalist):
                                        str_hi = ''.join(hiraganalist)
                                        new_hiList.append(str_hi)
                                
                                    
                    # print(new_kList, hiraganalist)
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

            try:
                pass
            except:
                pass
            
            if ('記号' in data[i][4]):
                conj = False
            
            if conj:
                if '終止形' in data[i][6]:
                    inputKata = True
                    conj = False
                    # if '助動詞-マス' in 
                pass

            if inputKata:
                temp = [kata, [], [], [], []]
                if kanji:
                    temp[1] = kanji
                if katadasar:
                    if '接尾辞' in data[i][4] and not ((data[i][0] in katadasar[0]) or (data[i][3] in katadasar[0])):
                        katadasar[0] += data[i][0]
                        katadasar[1] += data[i][1] 
                    katadasar[1] = self.convKanaRo(katadasar[1], 'hiragana')
                    temp[2] = katadasar

                else:
                    if (combine_count == 1):
                        katadasar = [data[i][3], data[i][2]]
                        katadasar[1] = self.convKanaRo(katadasar[1], 'hiragana')
                        temp[2] = katadasar
                        if ('意志推量形' in data[i][6]):
                            katadasar = [data[i][0], data[i][1]]
                            katadasar[1] = self.convKanaRo(katadasar[1], 'hiragana')
                            temp[2] = katadasar
                        if '記号' in data[i][4]:
                            temp[2] = []
                            temp[4] = 'symbol'
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
                prenoun = False

        return kelompokKata
        pass
# auxverb = 助動詞 / jodoushi (助動詞-list)
# list -> -マス, -ヌ, -デス, -ナイ, -タ
# auxverb マス formal, ヌ negative, デス to be/is
#
# noun + サ行変格 (する) -> verb
# 
# Custom
# 動詞-居る -> iru form = continuous = doing something
#
# important note:
# -マス
# -ヌ
# -サ行変格

if (__name__ == "__main__"):
    # filepath = os.path.abspath(os.path.dirname(__file__))
    # a = os.path.join(os.path.dirname(filepath), 'dic', 'unidic')
    # print(f'{filepath}')
    # print(filepath)
    parse = Parse()
    a = parse.segmentasiTeks("娘ちゃんクイズ", debug=True)
    # a = parse.convKanaRo('イー','romaji')
    # a = ['','助動詞']
    # if ('助詞' in a[1]):
    #     print(a)
    # a = parse.furigana('突っこん','すっこん')
    pprint(a)
    #姉っていう生き物って、どうしてあんなにも不器用なんですかね。なんかいつもナゾの壁と戦ってません? もっと楽に生きればいいのに。というわけでお兄ちゃん、そんな不器用なお殺ちゃんをよろしくですーゆ
    # ['生きれ', 'イキレ', 'イキル', '生きる', '動詞-一般', '上一段-カ行', '仮定形-一般'],
#  ['ば', 'バ', 'バ', 'ば', '助詞-接続助詞', '', ''],
#  ['いい', 'イー', 'ヨイ', '良い', '形容詞-非自立可能', '形容詞', '連体形-一般'],
    # a = parse.segmentasiTeksTest("仕事")
    # pprint(a)
    # print(parse.furigana('様々'))
    # for x in a:
    #     if x[1]:
    #         print(x[1]) 
