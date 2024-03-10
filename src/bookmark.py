import sqlite3
import sys
from ast import literal_eval
from pprint import pprint
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QSizePolicy, QFrame
from PyQt5.QtCore import Qt
from parsing import Parse

class BookmarkDB():



    def __init__(self) -> None:

        self.conn = None
        try:
            self.conn = sqlite3.connect("src/db/bookmark.db")
            sql = "PRAGMA foreign_keys=ON;"
            c = self.conn.cursor()
            c.execute(sql)
            self.conn.commit()
        except Exception as e:
            pass

    
    def create_table(self, conn=None):
        if self.conn:
            conn = self.conn

        CREATE_TABEL_KATA = """CREATE TABLE IF NOT EXISTS tabel_kata(
                        id_kata INTEGER PRIMARY KEY,
                        kata TEXT,
                        kanji TEXT,
                        hiragana TEXT,
                        romaji TEXT,
                        jlpt_lvl TEXT,
                        bahasa TEXT
                        );"""
        CREATE_TABEL_MAKNA = """CREATE TABLE IF NOT EXISTS tabel_makna(
                        id_makna INTEGER PRIMARY KEY,
                        tag1 TEXT,
                        tag2 TEXT,
                        makna TEXT,
                        id_kata INTEGER,
                        FOREIGN KEY (id_kata)
                            REFERENCES tabel_kata (id_kata) 
                            ON DELETE CASCADE
                        );"""
    

        try:
            c = conn.cursor()
            c.execute(CREATE_TABEL_KATA)
            c.execute(CREATE_TABEL_MAKNA)
        except Exception as e:
            pass

    def get_connection(self):
        return self.conn #sqlite3.connect("src/db/bookmark.db")
        pass

    
    def insert_bookmark(self, jisho_dat, bahasa='id' or 'en'):
        if self.conn:
            conn = self.conn

        cek_kata = ''
        
        
        sql1 = ''' INSERT INTO tabel_kata(kata,kanji,hiragana,romaji,jlpt_lvl,bahasa)
              VALUES(?,?,?,?,?,?) '''
        sql2 = ''' INSERT INTO tabel_makna(tag1,tag2,makna,id_kata)
              VALUES(?,?,?,?) '''

        kata = ''
        kanji = ''
        hiragana = ''
        romaji = ''
        jlpt = ''
        id_kata = None

        if jisho_dat[0]:
            kata = jisho_dat[0]
            kanji = jisho_dat[0]
            cek_kata = self.cari_kata(jisho_dat[0], jisho_dat[1], bahasa)
        else:
            if jisho_dat[1]:
                kata = jisho_dat[1]
                cek_kata = self.cari_kata(jisho_dat[1], jisho_dat[1], bahasa)

        if cek_kata:
            print('kata sudah ada dalam database')
            print('kata :', cek_kata[0][1])
            print('baca :', cek_kata[0][3])
            return
        
        if jisho_dat[1]:
            hiragana = jisho_dat[1]
            romaji = Parse.convKanaRo(hiragana, 'romaji')

        if jisho_dat[2]:
            jlpt = '[' + ', '.join(jisho_dat[2]) + ']'

        c = conn.cursor()
        c.execute(sql1, (kata,kanji,hiragana,romaji,jlpt,bahasa,))
        conn.commit()
        id_kata = c.lastrowid

        # print(id_kata)
        # print('kata : ', kata)
        # print('kanji : ',kanji)
        # print('hiragana : ',hiragana)
        # print('romaji : ',romaji)
        # print('jlpt : ',jlpt)
        # print()

        # return

        if jisho_dat[3]:
            for sense in jisho_dat[3]:
                # dibikin bentuk array string
                tag1 = ''
                tag2 = ''
                makna = ''
                if sense[0]: #tag1
                    tag1 += '['
                    for i in range(len(sense[0])):
                        tag1 += '["' + '", "'.join(sense[0][i]) + '"]'
                        try:
                            if sense[0][i+1]:
                                tag1 += ', '
                        except IndexError:
                            pass
                    tag1 += ']'
                    # tag1 = tag1.replace("'","''") #katanya escape kutip = 2 kutip
                    pass
                if sense[1]: #tag2 (part of speech)
                    tag2 += '['
                    for i in range(len(sense[1])):
                        tag2 += '["' + '", "'.join(sense[1][i]) + '"]'
                        try:
                            if sense[1][i+1]:
                                tag2 += ', '
                        except IndexError:
                            pass
                    tag2 += ']'
                    # tag2 = tag2.replace("'","''") #katanya escape kutip = 2 kutip
                    pass
                if sense[2]: #makna
                    # makna += ''                    
                    makna += '["' + '", "'.join(sense[2]) + '"]'
                    # makna += ''
                    # makna = makna.replace("'","''") #katanya escape kutip = 2 kutip
                    pass
                pass
                c.execute(sql2, (tag1,tag2,makna,id_kata))
                conn.commit()
                # print('tag1 : ',tag1)
                # print('tag2 : ',tag2)
                # print('makna : ',makna)
            pass
        return (id_kata, kata, hiragana, romaji, jisho_dat[3][0][2])

    def delete_bookmark(self, id_kata):
        if self.conn:
            conn = self.conn
        try:
            sql = "DELETE FROM tabel_kata WHERE id_kata=?;"
            c = conn.cursor()
            c.execute(sql, (id_kata,))
            conn.commit()
        except Exception as e:
            print(e)
        pass

    # menampilkan data bookmark pada layar tampilan
    def showall_bookmark(self):
        if self.conn:
            conn = self.conn

        sql1 = "SELECT * FROM tabel_kata"
        sql2 = "SELECT makna FROM tabel_makna WHERE id_kata=?"

        c = conn.cursor()
        c.execute(sql1)
        rows = c.fetchall()
        makna = []

        for row in rows:
            c.execute(sql2, (row[0],))
            makna.append(literal_eval(c.fetchone()[0]))
            pass
        return (rows, makna)
        pass

    def cari_kata(self, kata, hiragana, bahasa):
        if self.conn:
            conn = self.conn
        c = conn.cursor()
        c.execute("SELECT * FROM tabel_kata WHERE kata=? AND hiragana=? AND bahasa=?",(kata,hiragana,bahasa,))
        rows = c.fetchall()
        try:
            return rows
        except IndexError:
            return rows
        pass

    def get_data(self, id_kata):
        if self.conn:
            conn = self.conn
        c = conn.cursor()
        c.execute("SELECT * FROM tabel_kata WHERE id_kata=?", (id_kata,))
        kata = c.fetchall()
        c.execute("SELECT * FROM tabel_makna WHERE id_kata=?", (id_kata,))
        makna = c.fetchall()
        return (kata, makna)
        pass

class BookmarkWidget(QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName('a')
        # fonr 'Yu Gothic UI' atau 'Meiryo UI'
        styleSheet = '''
                    .QLabel{
                        font-family: 'Yu Gothic UI';
                    }
                    #kata{
                        font-size: 14px;
                    }
                    #caraBaca{
                        font-size: 12px;
                    }
                    #makna{
                        font-size: 15px
                    }
                    #detailTxt{
                        font-size: 12px;
                        color: rgba(19, 120, 198, 1);
                        text-decoration: underline;
                    }
                    #detailTxt:hover{
                        color: rgba(255, 120, 198, 1);
                    '''
        self.setStyleSheet(styleSheet)
        
        self.setMaximumHeight(80)
        self.setMinimumHeight(80)

        self.checkboxWidget = QWidget()
        self.left_cont = QWidget()
        self.right_cont = QWidget()

        self.cbLayout = QHBoxLayout()
        self.main_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.right_layout = QHBoxLayout()

        self.checkBox = QCheckBox()
        self.kata = QLabel() #kata
        self.kata.setObjectName('kata')
        self.caraBaca = QLabel() # hiragana (romaji)
        self.caraBaca.setObjectName('caraBaca')
        self.makna = QLabel() # makna
        self.makna.setObjectName('makna')
        self.detailTxt = QLabel() # lihat detail
        self.detailTxt.setObjectName('detailTxt')
        self.detailTxt.setCursor(Qt.PointingHandCursor)
        self._id_kata = QLabel()

        # test isi
        self.checkBox.setText('')
        self.kata.setText('IniKata')
        self.caraBaca.setText('IniCaraBaca')
        self.makna.setText('IniMakna')
        self.makna.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.detailTxt.setText('Detail >')
        self._id_kata.setText('iniIDKATA')

        self.cbLayout.addWidget(self.checkBox)
        self.cbLayout.setContentsMargins(0,0,2,0)
        self.checkboxWidget.setLayout(self.cbLayout)
        self.checkboxWidget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        self.left_layout.addWidget(self.kata)
        self.left_layout.addWidget(self.caraBaca)
        self.left_cont.setLayout(self.left_layout)
        self.left_cont.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.right_layout.addWidget(self._id_kata)
        self.right_layout.addWidget(self.makna)
        self.right_layout.addWidget(self.detailTxt)
        self.right_layout.setAlignment(Qt.AlignRight)
        self.right_cont.setLayout(self.right_layout)
        self.left_cont.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.main_layout.addWidget(self.checkboxWidget)
        self.main_layout.addWidget(self.left_cont)
        self.main_layout.addWidget(self.right_cont)

        self.setLayout(self.main_layout)

        self._id_kata.setVisible(False)
    
    # def checkCheckbox(self, state):
    #     if state == 2:  # Qt.Checked

    #     else:

    #     pass



if __name__ == "__main__":
    jishodat1 = """['','じゃない',[],[[[['biasanya ditulis dengan kana saja', 'uk']],[['expressions (phrases, clauses, etc.)', ''],["kata sifat bentuk 'i'", 'i-adj']],['tidak', 'saya tidak']],[[['biasanya ditulis dengan kana saja', 'uk']],[['expressions (phrases, clauses, etc.)', ''],["kata sifat bentuk 'i'", 'i-adj']],['Bukan?']]]] """
    jishodat2 = '''['勉強', 'べんきょう', ['jlpt-n3', 'jlpt-n5'], [[[], [['nomina', 'n'], ["nomina yang menjadi kata kerja dengan 'suru'", 'vs'], ['kata kerja transitif', 'vt']], ['belajar']], [[], [['nomina', 'n'], ["nomina yang menjadi kata kerja dengan 'suru'", 'vs'], ['kata kerja intransitif', 'vi']], ['ketekunan', 'bekerja keras']], [[], [['nomina', 'n']], ['pengalaman', 'Pelajaran (untuk masa depan)']], [[], [['nomina', 'n'], ["nomina yang menjadi kata kerja dengan 'suru'", 'vs'], ['kata kerja transitif', 'vt'], ['kata kerja intransitif', 'vi']], ['diskon', 'penurunan harga']]]]'''
    # pprint(literal_eval(jishodat))
    app = QApplication(sys.argv)
    # database = QFontDatabase()
    # print(database.families())
    db = BookmarkDB()
    # a = db.cari_kata('泳','およぐ','id')
    # print(a)
    # db.create_table()
    # db.show()
    db.insert_bookmark(literal_eval(jishodat1),'id')
    db.insert_bookmark(literal_eval(jishodat2),'id')
    # db.show()
    # id_kata, kata, kanji, hiragana, romaji, jlpt = db.cari_kata('じゃない')
    # print(kata)
    # wid = BookmarkWidget()
    # wid.show()
    app.exec_()

    pass