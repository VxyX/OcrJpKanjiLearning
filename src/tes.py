import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTextBrowser, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDesktopServices, QTextCursor

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        central_widget = QWidget()
        layout = QVBoxLayout()

        # Buat QTextBrowser
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setOpenLinks(True)
        text_browser.setHtml("a <a href='action_a'>b</a> c <a href='action_b'>d</a> e")

        # Tambahkan QTextBrowser ke layout
        layout.addWidget(text_browser)

        # Menangani tindakan yang sesuai untuk setiap tautan
        text_browser.anchorClicked.connect(self.handle_link_click)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def handle_link_click(self, url):
        link = url.toString()
        if link == "action_a":
            print("A clicked")
            # Tindakan atau perintah untuk huruf 'a'
        elif link == "action_b":
            print("B clicked")
            # Tindakan atau perintah untuk huruf 'b'
        self.centralWidget().findChild(QTextBrowser).setHtml("a <a href='action_a'>b</a> c <a href='action_b'>d</a> e")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
