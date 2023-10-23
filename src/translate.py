from googletrans import Translator, LANGUAGES

def translate_text(text, target_lang):
    translator = Translator()

    if target_lang in LANGUAGES:
        translated = translator.translate(text, src='ja', dest=target_lang)
        return translated.text
    else:
        return "Bahasa tujuan tidak valid."
    

text_to_translate = "【原神】 原神においてフレームレートはめっちゃ大事"
translated_text_en = translate_text(text_to_translate, "en")
# print(f'Translated to English: {translated_text_en}')