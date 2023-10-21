import requests
import xml.etree.ElementTree as ET
import os
import svgwrite
import tkinter as tk
from PIL import Image, ImageTk
import io
from svg.path import parse_path

cwd = os.getcwd()  # Get the current working directory (cwd)
files = os.listdir(cwd)  # Get all the files in that directory
print("Files in %r: %s" % (cwd, files))


# Fungsi untuk mencari makna kata di Jisho menggunakan Jisho API
def search_jisho(word):
    url = f"https://jisho.org/api/v1/search/words?keyword={word}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data["meta"]["status"] == 200 and data["data"]:
            # Ambil data pertama (paling relevan)
            result = data["data"][0]
            japanese_word = result["japanese"][0]["word"]
            meanings = [", ".join(sense["english_definitions"]) for sense in result["senses"]]
            return japanese_word, meanings
        else:
            return "Kata tidak ditemukan di Jisho."
    else:
        return "Terjadi kesalahan dalam mengakses API Jisho."

# Fungsi untuk mendapatkan informasi stroke order dari KanjiVG menggunakan KanjiVG API
def get_kanjivg_data(karakter):
    # Membaca file XML
    
    
    import traceback
    # ...
    try:
        tree = ET.parse("./src/kanjivg.xml")
        root = tree.getroot()
        # ...
    except IOError:
        ex_info = traceback.format_exc()
        print('ERROR!!! Check if this file exists and you have right to read it!')
        print('ERROR!!! Exception info:\n%s' % (ex_info))



    karakter_id = ord(karakter)
    if karakter_id > 0xf and karakter_id <= 0xfffff:
        karakter_id = "kvg:kanji_%05x" % (karakter_id)
    
    # List untuk menyimpan urutan stroke karakter yang cocok
    urutan_strokes = []
    
    # Melakukan iterasi pada setiap elemen kanji dalam data SVG
    for kanji_elem in root.findall(".//kanji"):
        # Mendapatkan karakter kanji
        kanji_id = kanji_elem.get("id")
        
        # Jika karakter kanji cocok dengan yang dicari
        if kanji_id == karakter_id:
            # Menambahkan urutan stroke ke dalam list urutan_strokes
            for path in kanji_elem.findall(".//path"):
                urutan_strokes.append(path.get("d"))
    
    return urutan_strokes

def buat_gambar_svg_dinamis(path_data):
    dwg = svgwrite.Drawing(size=(300, 300), debug=False)

    # Membuat elemen 'g' untuk elemen statis
    static_group = dwg.g()
    static_group['style'] = "fill:none;stroke:#000000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;"
    dwg.add(static_group)

    # Tambahkan setiap path ke dalam elemen SVG
    for data in path_data:
        # temp = data.replace(',',' ')
        data = parse_path(data).d()
        anim_path = static_group.add(dwg.path(d=data))
        # anim_path = anim_group.add(dwg.path())
        anim_path['d'] = data
        anim_path.add(dwg.animateMotion(
        begin="0s", dur="5s", repeatCount="indefinite",
        keyPoints="0%;100%;0%",
        keyTimes="0;0.5;1"
        ))
        # path = svgwrite.path.Path(d=data)
        # path.fill("none").stroke("black", 2)
        # dwg.add(path)
    dwg.save()

# Fungsi ini akan menampilkan gambar SVG di antarmuka Tkinter
# def tampilkan_gambar_svg_dinamis(path_data):
#     svg_data = buat_gambar_svg_dinamis(path_data)

#     # Buat gambar dari data SVG
#     img = Image.open(io.BytesIO(svg_data.encode()))
#     img = ImageTk.PhotoImage(img)

#     # Buat jendela Tkinter
#     root = tk.Tk()

#     # Buat label untuk menampilkan gambar
#     label = tk.Label(root, image=img)
#     label.pack()

#     # Tampilkan jendela
#     root.mainloop()


# Contoh penggunaan:
search_word = "猫"  # Kata yang ingin dicari di Jisho
kanji_character = "猫"  # Kanji yang ingin dicari stroke ordernya di KanjiVG
strokes = get_kanjivg_data(search_word)
# print(type(strokes[0]))
buat_gambar_svg_dinamis(strokes)
# Cari makna kata di Jisho
# japanese_word, meanings = search_jisho(search_word)
# print(f"Makna kata {japanese_word}: {', '.join(meanings)}")

# Dapatkan data stroke order dari KanjiVG
