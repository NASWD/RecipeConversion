from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import QRectF

class GenerateWaferTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        title = QLabel("🧠 Wafer Visualization")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #f0f0f0; padding: 8px 0;")
        layout.addWidget(title)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet("background-color: #111;")
        self.view.setFixedHeight(400)
        layout.addWidget(self.view)

        self.setLayout(layout)
        self.draw_placeholder_map()

    def draw_placeholder_map(self):
        spacing = 20
        die_radius = 6
        wafer_map = [
            (0, 0, 'A'), (1, 0, 'D'), (-1, 0, 'B'),
            (0, 1, 'A'), (1, 1, 'A'), (-1, 1, 'X')
        ]

        for x, y, status in wafer_map:
            color = QColor('gray')
            if status == 'A': color = QColor('#4f90ff')
            elif status == 'D': color = QColor('red')
            elif status == 'B': color = QColor('orange')
            elif status == 'X': color = QColor('#444')

            ellipse = QGraphicsEllipseItem(QRectF(x * spacing, y * spacing, die_radius * 2, die_radius * 2))
            ellipse.setBrush(QBrush(color))
            self.scene.addItem(ellipse)