class Translate():
    def __init__(self):
        self.ts = None
        self.err = None
        try:
            import translators as ts
            self.ts = ts
            self.err = None
        except Exception as e:
            self.err = "Connection Error"

    def translate(self, text, target_lang, from_lang='ja', translator='bing'):
        
        if self.err:
            try:
                import translators as ts
                self.ts = ts
                self.err = None
            except Exception as e:
                return self.err
        
        try:
            translated = self.ts.translate_text(text, translator=translator,from_language=from_lang, to_language=target_lang)
        except Exception as e:
            translated = "Connection Error"

        return translated

        

if __file__ == '__main__':
    # print(ts.get_languages())
    text_to_translate = "speed; velocity; pace; rate"
    tl = Translate.translate(Translate(), text_to_translate, translator='google', from_lang='en', target_lang='id')
    a = Translate()
    language = a.ts.get_languages()
    print(language)
    # print('tes')
    print(tl)
    # translated_text_en = translate_text(text_to_translate, "bing", "en")
    # print(f'Translated to English: {translated_text_en}')