import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QListWidget, QListWidgetItem,
    QWidget, QHBoxLayout
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

from ui.home_tab import HomeTab
from ui.wafer_map_tab import WaferMapTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FM Recipe Generator")
        self.setGeometry(100, 100, 1200, 700)
        self.init_dark_mode()

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.insertItem(0, QListWidgetItem("Home"))
        self.sidebar.insertItem(1, QListWidgetItem("Wafer Map"))
        self.sidebar.setFixedWidth(180)

        # Stack of tabs
        self.stack = QStackedWidget()
        self.home_tab = HomeTab()
        self.wafer_map_tab = WaferMapTab()

        self.stack.addWidget(self.home_tab)
        self.stack.addWidget(self.wafer_map_tab)

        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def init_dark_mode(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(33, 33, 33))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Highlight, QColor(142, 45, 197))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        QApplication.setPalette(palette)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
