from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtGui import QIcon
import sys
import os


class DragDropWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Set Icon
        icon_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'assets', 'icons', 'nordson-icon.jpg'))
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Nordson Recipe Conversion")
        self.setGeometry(100, 100, 600, 400)
        self.setAcceptDrops(True)
        self.file_paths = []
        self.label = QLabel("Drag and drop files here", self)
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.apply_dark_mode()

    def apply_dark_mode(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)

        self.setPalette(dark_palette)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        paths = [url.toLocalFile() for url in urls]

        if len(paths) + len(self.file_paths) > 4:
            self.label.setText("Error: You can only upload 4 files total.")
            # Only accept files that end with the following extensions:
            # fluid file (.flu)
            # vision file (.avw)
            # heater files (.htr)
            # wafer map (.rcp)
            # Notice [This file is not in the correct format.]
            return

        self.file_paths.extend(paths)
        display = "\n".join(os.path.basename(p) for p in self.file_paths)
        self.label.setText(f"Files uploaded ({len(self.file_paths)}/4):\n{display}")


# For testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DragDropWindow()
    window.show()
    sys.exit(app.exec_())
