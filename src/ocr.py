import pytesseract
from PIL import Image
import os
import cv2

class Ocr():
    def __init__(self, image=None):
        
        # menentukan path tesseract
        main_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
        self.tesseract_path = os.path.abspath(os.path.join(main_dir, 'tesseract', 'tesseract.exe'))
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        self.jp_trained_data_best = main_dir + '/src/tesseract/tessdata_best'
        self.config = f'--oem 1 -c preserve_interword_spaces=1 --tessdata-dir "{self.jp_trained_data_best}"'

        if image:
            self.img = image
        else:
            self.img = r'screenshot.png'
        # print('\n\n\nimage file name :',self.img)

    def getText(self, img=None):
        if not img:
            img = self.img
        image = Image.open(img)
        lang = 'jpn'
        
        text = pytesseract.image_to_string(image, lang, config=self.config)
        # print(img)
        return text
    
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

    
    
if __name__ == "__main__":
    c = Ocr('')
    # c.imgPreProcessing()
    print()
    print('output text: ', c.getText('screenshot.png'))
    # a = '--oem 1 -c preserve_interword_spaces=1 --tessdata-dir "{}"'
    # main_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
    # a = f'--oem 1 -c preserve_interword_spaces=1 --tessdata-dir "{main_dir}"'
    # print(a)
    # print('inverted:')
    # print(c.getText('inverted.jpg'))
    # print('\nbw:')
    # print(c.getText('bw.jpg'))
    # print('\nno_noise:')
    # print(c.getText('no_noise.jpg'))
    # print('\nno_noise_inv:')
    # print(c.getText('no_noise_inv.jpg'))