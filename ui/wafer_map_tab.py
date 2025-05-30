from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFormLayout, QDoubleSpinBox,
    QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsRectItem
)
from PyQt5.QtGui import QPen, QColor, QPainter
from PyQt5.QtCore import Qt, QRectF
import os

class WaferMapTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        left_panel = QVBoxLayout()
        right_panel = QVBoxLayout()

        # Form inputs
        self.inputs = {}
        form = QFormLayout()
        for label in ["Wafer Diameter (mm)", "Grid X Size", "Grid Y Size",
                      "Grid X Pitch (mm)", "Grid Y Pitch (mm)",
                      "Package Width (mm)", "Package Height (mm)"]:
            box = QDoubleSpinBox()
            box.setRange(0, 1000)
            default = 15 if "Pitch" in label or "Package" in label else 300 if "Wafer" in label else 19
            box.setValue(default)
            form.addRow(label, box)
            self.inputs[label] = box
        left_panel.addLayout(form)

        # File loader
        self.map_file_label = QLabel("No wafer map loaded.")
        self.map_file_label.setStyleSheet("color: white;")
        browse_btn = QPushButton("Browse Wafer Map File")
        browse_btn.clicked.connect(self.load_map_file)
        left_panel.addWidget(self.map_file_label)
        left_panel.addWidget(browse_btn)

        # Table for map entries
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Part ID", "X ID", "Y ID", "Left", "Top", "Right", "Bottom"])
        left_panel.addWidget(self.table)

        # Wafer drawing canvas
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setStyleSheet("background-color: white; border: 1px solid white;")
        right_panel.addWidget(self.view)

        layout.addLayout(left_panel, 3)
        layout.addLayout(right_panel, 2)
        self.setLayout(layout)

    def load_map_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Wafer Map", "", "Text Files (*.txt);;All Files (*)")
        if not path:
            return
        self.map_file_label.setText(os.path.basename(path))
        self.populate_table_from_file(path)
        self.draw_wafer_preview()

    def populate_table_from_file(self, path):
        with open(path, 'r') as f:
            content = f.read().replace('\n', '')
        entries = content.split(';')
        self.table.setRowCount(len(entries))
        for i, entry in enumerate(entries):
            parts = entry.strip().split(',')
            if len(parts) != 4:
                continue
            part_id, x, y, status = parts
            for col, val in enumerate([part_id, x, y, '', '', '', '']):
                item = QTableWidgetItem(val)
                self.table.setItem(i, col, item)

    def draw_wafer_preview(self):
        self.scene.clear()
        # Get values
        diameter = self.inputs["Wafer Diameter (mm)"].value()
        pitch_x = self.inputs["Grid X Pitch (mm)"].value()
        pitch_y = self.inputs["Grid Y Pitch (mm)"].value()
        grid_x = int(self.inputs["Grid X Size"].value())
        grid_y = int(self.inputs["Grid Y Size"].value())
        pkg_w = self.inputs["Package Width (mm)"].value()
        pkg_h = self.inputs["Package Height (mm)"].value()

        # Draw wafer circle
        wafer_radius = diameter / 2
        wafer_circle = QGraphicsEllipseItem(QRectF(-wafer_radius, -wafer_radius, diameter, diameter))
        wafer_circle.setPen(QPen(QColor("lime"), 1))
        self.scene.addItem(wafer_circle)

        # Draw dies
        origin_x = - (grid_x / 2) * pitch_x
        origin_y = - (grid_y / 2) * pitch_y

        for i in range(grid_x):
            for j in range(grid_y):
                cx = origin_x + i * pitch_x
                cy = origin_y + j * pitch_y
                die_rect = QRectF(cx, cy, pkg_w, pkg_h)
                center_dist_sq = (cx + pkg_w/2)**2 + (cy + pkg_h/2)**2
                if center_dist_sq <= wafer_radius**2:
                    rect = QGraphicsRectItem(die_rect)
                    rect.setPen(QPen(QColor("black"), 0.5))
                    self.scene.addItem(rect)
