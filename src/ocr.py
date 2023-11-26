import pytesseract
from PIL import Image

class Capture():
    def __init__(self, image):
        
        # menentukan path tesseract
        self.tesseract_path = r'D:\\Program Files\\Tesseract\\tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        self.jp_trained_data ='--tessdata-dir "D:/Bakup/Materi/Semester9/Skripsi/program/orcjplearning/src/tesseract/tessdata"'

        if image:
            self.img = image
        else:
            self.img = r'screenshot.png'

        pass
    
    def imgPreProcessing(self):
        pass

    def getText(self):
        image = Image.open(self.img)
        lang = 'jpn'

        # Terapkan OCR pada gambar menggunakan pytesseract
        text = pytesseract.image_to_string(image, lang)

        return text