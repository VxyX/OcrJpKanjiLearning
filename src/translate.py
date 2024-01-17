

import threading

class Translate():
    def __init__(self):
        self.ts = None
        self.err = None
        try:
            import translators as ts
            self.ts = ts
        except Exception as e:
            self.err = "Connection Error"
            pass
        pass
    def translate(self, text, target_lang, from_lang='ja', translator='bing'):
        
        if self.err:
            translated = "Connection Failed"
            return translated
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

        

if __file__ == '__main__':
    # print(ts.get_languages())
    text_to_translate = "speed; velocity; pace; rate"
    tl = Translate.translate(Translate(), text_to_translate, translator='google', from_lang='en', target_lang='id')
    # print('tes')
    print(tl)
    # translated_text_en = translate_text(text_to_translate, "bing", "en")
    # print(f'Translated to English: {translated_text_en}')