import pytesseract
import cv2
from PIL import Image

class Capture():
    def __init__(self, image):
        
        # menentukan path tesseract
        self.tesseract_path = r'D:\\Program Files\\Tesseract\\tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        self.jp_trained_data ='--oem 1 -c preserve_interword_spaces=1 --tessdata-dir "D:/Bakup/Materi/Semester9/Skripsi/program/orcjplearning/src/tesseract/tessdata"' #normal accuracy normal speed
        self.jp_trained_data_best = '--oem 1 -c preserve_interword_spaces=1 --tessdata-dir "D:/Bakup/Materi/Semester9/Skripsi/program/orcjplearning/src/tesseract/tessdata_best"' #best accuracy slow speed
        print(pytesseract.get_tesseract_version())
        if image:
            self.img = image
        else:
            self.img = r'screenshot.png'

        pass
    
    def imgPreProcessing(self):
        img = cv2.imread(self.img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret,thresh1 = cv2.threshold(img,179,255,cv2.THRESH_BINARY)
        inverted_image = cv2.bitwise_not(thresh1)
        no_noise_inv = self.noise_removal(inverted_image)
        no_noise = self.noise_removal(thresh1)
        # dilated_image = self.thick_font(no_noise_inv)
        # cv2.imwrite("dilated_image.jpg", dilated_image)
        cv2.imwrite("no_noise_inv.jpg", no_noise_inv)
        cv2.imwrite("no_noise.jpg", no_noise)
        cv2.imwrite("inverted.jpg", inverted_image)
        cv2.imwrite("bw.jpg", thresh1)
        return None
        pass
    
    def thick_font(self, image):
        import numpy as np
        image = cv2.bitwise_not(image)
        kernel = np.ones((2,2),np.uint8)
        image = cv2.dilate(image, kernel, iterations=1)
        image = cv2.bitwise_not(image)
        return (image)

    def noise_removal(self, image):
        import numpy as np
        kernel = np.ones((1, 1), np.uint8)
        image = cv2.dilate(image, kernel, iterations=1)
        kernel = np.ones((1, 1), np.uint8)
        image = cv2.erode(image, kernel, iterations=1)
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        image = cv2.medianBlur(image, 3)
        return (image)

    def getText(self, img=None):
        if not img:
            img = self.img
        image = Image.open(img)
        lang = 'jpn'

        # Terapkan OCR pada gambar menggunakan pytesseract
        text = pytesseract.image_to_string(image, lang, config=self.jp_trained_data_best)
        print(img)
        return text
    
if __name__ == "__main__":
    c = Capture('')
    c.imgPreProcessing()
    print('normal:')
    print(c.getText('screenshot.png'))
    print('inverted:')
    print(c.getText('inverted.jpg'))
    print('\nbw:')
    print(c.getText('bw.jpg'))
    print('\nno_noise:')
    print(c.getText('no_noise.jpg'))
    print('\nno_noise_inv:')
    print(c.getText('no_noise_inv.jpg'))