import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImageReader, QImage
from PyQt5.QtWidgets import  QApplication, QMainWindow, QLabel, QSlider, QVBoxLayout, QWidget, QPushButton, QFileDialog
import cv2
from PIL import Image, ImageQt

class ImageThresholdingApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Image Thresholding App")

        # Widget utama
        widget = QWidget(self)
        self.setCentralWidget(widget)

        # Layout utama
        layout = QVBoxLayout(widget)

        # Label untuk menampilkan gambar
        self.image_label = QLabel(self)
        self.image_label.setScaledContents()
        layout.addWidget(self.image_label)

        # Slider untuk mengatur nilai threshold
        self.threshold_slider = QSlider(Qt.Horizontal, self)
        self.threshold_slider.setRange(0, 255)
        layout.addWidget(self.threshold_slider)

        # Tombol untuk memuat gambar
        load_button = QPushButton("Load Image", self)
        load_button.clicked.connect(self.load_image)
        layout.addWidget(load_button)

        # Menghubungkan perubahan slider dengan fungsi update threshold
        self.threshold_slider.valueChanged.connect(self.update_threshold)

        # Inisialisasi variabel gambar
        self.image = None

    def load_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        # Memilih gambar dari dialog file
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp);;All Files (*)", options=options)

        if file_name:
            # Membaca gambar menggunakan OpenCV
            self.image = cv2.imread(file_name)
            self.image1 = self.image
            self.image_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

            # Menampilkan gambar
            self.display_image(self.image)

    def display_image(self, image):
        # Konversi gambar OpenCV ke QImage
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channel = image_rgb.shape
        bytes_per_line = 3 * width
        q_image = QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)

        # Menampilkan gambar di QLabel
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap)

    def update_threshold(self):
        # Menerapkan thresholding pada gambar
        
        _, thresholded_image = cv2.threshold(self.image_gray, self.threshold_slider.value(), 255, cv2.THRESH_BINARY)

        # Menampilkan gambar yang telah diterapkan thresholding
        self.image1 = thresholded_image
        if self.threshold_slider.value() == 0:
            self.image1 = self.image
        self.display_image(self.image1)

def main():
    app = QApplication(sys.argv)
    window = ImageThresholdingApp()
    window.setGeometry(100, 100, 800, 600)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
