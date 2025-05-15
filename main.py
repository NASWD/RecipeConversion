import sys
from PyQt5.QtWidgets import QApplication
from views.main_window import DragDropWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DragDropWindow()
    window.show()
    sys.exit(app.exec_())
