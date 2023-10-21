import MeCab
import sqlite3
import sys
import pytesseract
from PIL import Image

# determine tesseract path
tesseract_path = r'D:\\Program Files\\Tesseract\\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = tesseract_path

# jp dictionary for MeCab
unidic = r'D:\\Bakup\\Materi\\Semester9\\Skripsi\\program\\ocrjplearning\\dic\\unidic'
ipadic = r'D:\\Bakup\\Materi\\Semester9\\Skripsi\\program\\ocrjplearning\\dic\\ipadic'

tagger = MeCab.Tagger(f"-d {unidic}")

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
text = "聞えるんだよ"


image = Image.open('screenshot_340.png')
lang = 'jpn'

# Terapkan OCR pada gambar menggunakan pytesseract
text = pytesseract.image_to_string(image, lang)

# text = text.split()
# text = text[2]

print(text)
result = tagger.parse(text) #or parseNBest(n, text)
# print(result)
result = result.splitlines() #splitLines untuk pengelompokan
# print(result)


# d = tagger.dictionary_info()
# while d:
#         print ("filename: %s" % d.filename)
#         print ("charset: %s" %  d.charset)
#         print ("size: %d" %  d.size)
#         print ("type: %d" %  d.type)
#         print ("lsize: %d" %  d.lsize)
#         print ("rsize: %d" %  d.rsize)
#         print ("version: %d" %  d.version)
#         d = d.next

data = []

for line in result:
    values = line.split('\t')  # Memisahkan nilai dalam setiap baris berdasarkan tab ('\t')
    if (values == ['EOS']):
        continue
    data.append(values)  # Menambahkan nilai-nilai ke dalam list data
print(data)

conjVerb = False
# dataiter = iter(data)
next_data_row = None

pemisahankata = []
kelompokkatakerja = []
inputkata = False
kata = ''
skip = False

for i in range(len(data)):
    # if skip:
    #     skip = False
    #     continue
    if (data[i][5]):
        kelompokkatakerja.append(data[i][5])

    if ('サ変可能' in data[i][4]):
        # conjVerb = True
        if ('非自立可能' in data[i+1][4] or '接尾辞' in data[i+1][4]):
            conjVerb = True

    # combine verb 連用形 (renkyoukei/continuous form), 連体詞 (rentaishi/pre-noun adjectival/pronomina)
    # 助詞-準体助詞 ()
    if ('連用形' in data[i][6] or '連体詞' in data[i][4] or '助詞-準体助詞' in data[i][4] or '未然形' in data[i][6]):
        conjVerb = True
        try:
            if ('連体詞' in data[i][4] and ('名詞-普通名詞-一般' in data[i+1][4] or '名詞' not in data[i+1][4])):
                conjVerb = False
        except IndexError as e:
            pass
    
    # fix combined phrase with non-independent verb and final-form also not actially verb
    # ex : ある can be verb or pronomina
    try:
        if ('非自立' in data[i+1][4] and not data[i+1][5]):
            conjVerb = True 
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
    if conjVerb:
        inputkata = False
        kata += data[i][0]
        try:
            if ('助動詞' in data[i][4]):
        #     # kata += data[0]
                conjVerb = False
                inputkata = True
                # fix multiple auxverb and continuous form
                if ('助動詞' in data[i+1][4] or '接続助詞' in data[i+1][4]):
                        conjVerb = True
                        inputkata = False

            # fix adjective and adverb combination
            if ('形状詞' in data[i][4] or '副詞' in data[i][4]):
                if ('助動詞' in data[i+1][4]):
                    conjVerb = True
                    inputkata = False
                else :
                    conjVerb = False
                    inputkata = True
                    
            # fix noun suffix like 者 (orang) -> 冒険者 (Petualang) 医者 (Dokter)
            if ('接尾辞' in data[i][4] and 'サ変可能' in data[i-1][4]):
                inputkata = True
                conjVerb = False

            # fix conjuctive particle -Te that has 非自立 (non-independent) form on the next iteration
            # ex : 聞こえてきて [kikoe(verb -> base = 聞く) -te(particle) -ki(non-independent) -te(particle)]
            if ('接続助詞' in data[i][4]):
                if ('非自立' not in data[i+1][4]):
                    conjVerb = False
                    inputkata = True

            if ('非自立可能' in data[i][4]):
                inputkata = True
                conjVerb = False
                if ('助動詞' in data[i+1][4] or '非自立可能' in data[i+1][4] or '接続助詞' in data[i+1][4]):
            #     # kata += data[0]
                    conjVerb = True
                    inputkata = False

            if ('終助詞' in data[i][4]):
                conjVerb = False
                inputkata = True
               
        except IndexError as e:
            inputkata = True
        # if next_data_row:
        #     if ('終止形' in next_data_row[6]):
        #         conjVerb = False
        #         inputkata = True
        #     kata += next_data_row[0]
        #     next_data_row = None
    else :
        inputkata = True
        kata += data[i][0]
    
    # print(conjVerb, inputkata, kata)
    if inputkata:
        temp = kata
        if (kelompokkatakerja):
            temp = [kata, kelompokkatakerja]
        pemisahankata.append(temp)
        kata = ''
        kelompokkatakerja = []

print(pemisahankata)


    
    
        
    