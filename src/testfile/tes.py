import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageThresholdingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Thresholding App")

        # Variabel untuk menyimpan nilai threshold
        self.threshold_value = tk.DoubleVar()

        # Inisialisasi UI
        self.create_widgets()

    def create_widgets(self):
        # Tombol untuk memuat gambar
        load_button = tk.Button(self.root, text="Load Image", command=self.load_image)
        load_button.pack(pady=10)

        # Scrollbar untuk mengatur nilai threshold
        threshold_label = tk.Label(self.root, text="Threshold Value:")
        threshold_label.pack()
        threshold_slider = tk.Scale(self.root, from_=0, to=255, orient="horizontal", variable=self.threshold_value, command=self.update_threshold)
        threshold_slider.pack()

        # Tampilan untuk menampilkan gambar
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack()

    def load_image(self):
        # Memuat gambar dari file
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            self.display_image()

    def update_threshold(self, _):
        # Menerapkan thresholding pada gambar dan menampilkan live preview
        _, thresholded_image = cv2.threshold(self.image, int(self.threshold_value.get()), 255, cv2.THRESH_BINARY)
        self.display_image(thresholded_image)

    def display_image(self, image=None):
        # Jika tidak ada gambar yang diberikan, gunakan gambar asli
        if image is None:
            image = self.image

        # Mengonversi gambar OpenCV ke format yang dapat ditampilkan oleh Tkinter
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_tk = ImageTk.PhotoImage(image_pil)

        # Menampilkan gambar di GUI
        self.canvas.config(width=image_tk.width(), height=image_tk.height())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
        self.canvas.image = image_tk

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageThresholdingApp(root)
    root.mainloop()
