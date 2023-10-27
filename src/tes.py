import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import Qt, QPropertyAnimation, QPointF, QRect
from PyQt5.QtGui import QPainterPath


class KanjiWritingAnimationExample(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Kanji Writing Animation Example')
        self.setGeometry(100, 100, 300, 300)

        self.svg_widget = QSvgWidget('src/05005-Kaisho-jlect.svg', self)
        self.animate_button = QPushButton('Animasikan', self)
        self.animate_button.clicked.connect(self.startAnimation)

        layout = QVBoxLayout()
        layout.addWidget(self.svg_widget)
        layout.addWidget(self.animate_button)

        self.setLayout(layout)

        # Animasi
        self.animation_duration = 100  # Durasi animasi per stoke (ms)
        self.stroke_paths = [
            [
                (52.25, 14),
                (51.73, 16.28),
                (51.73, 19.87),
                (49.93, 21.83),
                (44.73, 30.97)
            ],
            [
                (54.5, 19.25),
                (61.23, 26.55),
                (85.32, 51.36),
                (118.27, 83.27),
                (127.32, 87.66)
            ],
            [
                (37.36, 50.16),
                (39.00, 50.50),
                (43.04, 50.86),
                (47.02, 50.61),
                (51.68, 48.21),
                (71.34, 45.81),
                (91.00, 43.00),
                (94.04, 43.14)
            ],
            [
                (23, 65.98),
                (25.12, 66.50),
                (29.37, 67.14),
                (33.62, 67.44),
                (40.63, 67.58),
                (54.00, 68.72),
                (67.37, 69.00),
                (70.41, 69.14)
            ],
            [
                (47.16, 66.38),
                (47.78, 67.53),
                (47.75, 69.21),
                (46.83, 70.49),
                (41.66, 78.29),
                (33.64, 86.13),
                (31.53, 88.38)
            ],
            [
                (66.62, 77.39),
                (71.14, 80.62),
                (82.14, 93.35),
                (95.14, 106.08),
                (108.20, 110.90)
            ]
        ]

        self.animation_index = 0
        self.point_index = 0
        self.path = None

    def startAnimation(self):
        if self.animation_index < len(self.stroke_paths):
            path = QPainterPath()
            for points in self.stroke_paths:
                for point in points:
                    path.lineTo(QPointF(point[0], point[1]))
            print(path)
            
            self.svg_widget.renderer().setPath(path)
            self.svg_widget.update()
            # return
            self.stroke_animation = QPropertyAnimation(self.svg_widget, b'geometry')
            self.stroke_animation.setDuration(self.animation_duration)
            self.stroke_animation.setStartValue(QRect(10, 10, 100, 100))
            self.stroke_animation.setEndValue(QRect(50, 50, 200, 200))
            self.stroke_animation.finished.connect(self.continueAnimation)
            self.stroke_animation.start()
            self.animation_index += 1
        else:
            print("Animasi selesai")

    def continueAnimation(self):
        self.startAnimation()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = KanjiWritingAnimationExample()
    window.show()
    sys.exit(app.exec_())
