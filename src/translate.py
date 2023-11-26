

class Translate():
    def __init__(self):
        import translators as ts
        self.ts = ts
        pass
    def translate(self, text, translator, target_lang, from_lang='ja'):
        languages = self.ts.get_languages(translator)
        # print(languages)
        if target_lang in languages:
            try:
                translated = self.ts.translate_text(text, translator=translator,from_language=from_lang, to_language=target_lang)
            except Exception as e:
                print(e)
                translated = e
            return translated
        else:
            return "Bahasa tujuan tidak valid."

        
    
# print(ts.get_languages())
# text_to_translate = "ウマ娘イベント選択肢チエッカー (逆引き検索ツール)"
# tl = ts.translate_text(text_to_translate, translator='deepl', from_language='ja', to_language='en')
# print('tes')
# print(tl)
# translated_text_en = translate_text(text_to_translate, "bing", "en")
# print(f'Translated to English: {translated_text_en}')