from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow
import os

app = QApplication([])

# Inisialisasi window
window = QMainWindow()
window.setGeometry(100, 100, 800, 600)

# Menampilkan QWebEngineView di dalam window
print(os.getcwd())
view = QWebEngineView(window)
view.setUrl(QUrl.fromLocalFile('/src/teshtml.html'))
window.setCentralWidget(view)

window.show()

app.exec_()
