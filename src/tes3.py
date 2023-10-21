import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QGridLayout
from PyQt5.QtCore import Qt

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        central_widget = QWidget()
        layout = QVBoxLayout()

        # Text yang ingin ditampilkan
        text = "In publishing and graphic design, Lorem ipsum is a placeholder text commonly used to demonstrate the visual form of a document or a typeface without relying on meaningful content. Lorem ipsum may be used as a placeholder before final copy is available."

        # Pisahkan kata-kata
        words = text.split()

        # Buat layout horizontal untuk menampilkan QLabel
        h_layout = QGridLayout()

        for word in words:
            label = QLabel(word)
            h_layout.addWidget(label)

        # Tambahkan layout horizontal ke layout utama
        layout.addLayout(h_layout)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
