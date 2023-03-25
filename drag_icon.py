from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
from PIL import Image

img = Image.open('diagram.png')
diagram_width, diagram_height = img.size
print(diagram_width, diagram_height)


class OverlayImage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Overlay Image')
        self.setGeometry(100, 100, diagram_width, diagram_height)
        self.initUI()

    def initUI(self):
        # Set a background image
        self.bg_image = QPixmap('diagram.png')
        self.label_bg = QLabel(self)
        self.label_bg.setGeometry(0, 0, diagram_width, diagram_height)
        self.label_bg.setPixmap(self.bg_image)
        self.label_bg.setScaledContents(True)

        # Set an overlay image
        self.overlay_image = QPixmap('lock.png')
        self.label_overlay = QLabel(self)
        self.label_overlay.setGeometry(0, 0, 50, 50)
        self.label_overlay.setPixmap(self.overlay_image)
        self.label_overlay.setScaledContents(True)

        # Drag and drop images
        self.label_overlay.mousePressEvent = self.get_coords
        self.label_overlay.mouseReleaseEvent = self.place_image

    def get_coords(self, event):
        self.drag_start_x = event.x()
        self.drag_start_y = event.y()

    def place_image(self, event):
        self.drag_end_x = event.x()
        self.drag_end_y = event.y()

        self.label_overlay.move(self.drag_end_x - self.drag_start_x, self.drag_end_y - self.drag_start_y)

        # Save the image
        self.new_image = QPixmap(self.bg_image)
        painter = QPainter(self.new_image)
        painter.drawPixmap(self.drag_end_x - self.drag_start_x, self.drag_end_y - self.drag_start_y, self.overlay_image)
        painter.end()
        self.new_image.save('new_image.png')


app = QApplication(sys.argv)
ex = OverlayImage()
ex.show()
app.exec_()
