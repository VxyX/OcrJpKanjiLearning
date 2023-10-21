import pytesseract
from PIL import Image

class Capture():
    def __init__(self):
        
        # menentukan path tesseract
        self.tesseract_path = r'D:\\Program Files\\Tesseract\\tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path

        self.img = r'screenshot.png'

        pass
    
    @staticmethod
    def imgPreProcessing(self):
        pass

    def getText(self):
        image = Image.open(self.img)
        lang = 'jpn'

        # Terapkan OCR pada gambar menggunakan pytesseract
        text = pytesseract.image_to_string(image, lang)

        return text