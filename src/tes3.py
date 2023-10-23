def katakana_to_hiragana(katakana_text):
    hiragana_text = ""
    
    for character in katakana_text:
        katakana_code = ord(character)
        
        # Periksa apakah karakter adalah katakana
        if 0x30A1 <= katakana_code <= 0x30F6:
            # Kode hiragana adalah kode katakana - 96
            hiragana_code = katakana_code - 96 
            hiragana_character = chr(hiragana_code)
            hiragana_text += hiragana_character
        else:
            # Jika bukan karakter katakana, tambahkan karakter aslinya
            hiragana_text += character

    return hiragana_text

katakana_text = "コンニチハ"
hiragana_text = katakana_to_hiragana(katakana_text)

print(hiragana_text)
