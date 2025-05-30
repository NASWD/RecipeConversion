from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QHBoxLayout, QToolButton, QFrame, QSizePolicy, QHeaderView
)
from PyQt5.QtCore import Qt
import pandas as pd
from toast_widget import Toast
from fmw_builder import build_combined_fmw
import platform
import subprocess
from generate_fmw import generate_fmw_from_template
import os

def export_fmw(self):
    excel_path = [f for f in self.file_paths if f.endswith(".xlsx")][0]
    template_path = "/path/to/original/AutoTest Program.fmw"
    output_dir = os.path.dirname(excel_path)

    new_file = generate_fmw_from_template(excel_path, template_path, output_dir)
    self.label.setText(f"Exported:\n{os.path.basename(new_file)}")



class HomeTab(QWidget):
    def __init__(self):
        super().__init__()
        self.file_paths = []

        self.title = QLabel("Recipe Editor")
        self.title.setStyleSheet("font-size: 18px; font-weight: 500; color: #f0f0f0; padding: 4px 0;")

        self.file_list_layout = QVBoxLayout()
        self.file_list_layout.setSpacing(4)
        self.file_list_layout.setContentsMargins(4, 8, 4, 8)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.DoubleClicked)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)
        self.table.setFixedHeight(220)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setDefaultSectionSize(130)

        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.setShowGrid(True)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: white;
                font-size: 13px;
                border: 1px solid #444;
            }
            QHeaderView::section {
                background-color: #3a3a3a;
                color: white;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
        """)

        # Buttons
        self.load_button = QPushButton("Load Files")
        self.load_button.clicked.connect(self.open_file_dialog)
        self.export_button = QPushButton("Export")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.export_fmw)

        for btn in [self.load_button, self.export_button]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2e2e2e;
                    color: white;
                    border: 1px solid #444;
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #3a9ff1;
                    color: black;
                }
                QPushButton:disabled {
                    background-color: #555;
                    color: #aaa;
                }
            """)

        # Buttons in a row
        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        button_row.addStretch()
        button_row.addWidget(self.load_button)
        button_row.addWidget(self.export_button)
        button_row.addStretch()

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addLayout(self.file_list_layout)
        layout.addSpacing(10)
        layout.addWidget(self.table)
        layout.addLayout(button_row)
        layout.addStretch()
        self.setLayout(layout)

    def open_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Recipe Input Files",
            os.getcwd(),
            "All Files (*);;Excel (*.xlsx);;Text (*.txt);;Config (*.ini)"
        )
        if files:
            self.file_paths = list(set(self.file_paths + files))
            self.export_button.setEnabled(True)
            self.refresh_file_list()

            excel_file = next((f for f in self.file_paths if f.endswith(".xlsx")), None)
            if excel_file:
                self.display_excel(excel_file)

    def refresh_file_list(self):
        while self.file_list_layout.count():
            child = self.file_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for fpath in self.file_paths:
            fname = os.path.basename(fpath)
            file_row = QFrame()
            file_row.setStyleSheet("background-color: #2c2c2c; border-radius: 6px;")
            file_row.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            row_layout = QHBoxLayout(file_row)
            row_layout.setContentsMargins(8, 4, 8, 4)

            icon = QLabel("📄")
            icon.setStyleSheet("font-size: 12px; color: #aaa;")
            label = QLabel(fname)
            label.setFixedWidth(220)
            label.setWordWrap(False)
            label.setToolTip(fpath)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            label.setStyleSheet("color: white; font-size: 11px;")

            remove_btn = QToolButton()
            remove_btn.setText("❌")
            remove_btn.setStyleSheet("font-size: 10px; color: red; padding: 0 6px;")
            remove_btn.clicked.connect(lambda _, path=fpath: self.remove_file(path))

            row_layout.addWidget(icon)
            row_layout.addWidget(label)
            row_layout.addStretch()
            row_layout.addWidget(remove_btn)

            self.file_list_layout.addWidget(file_row)

    def remove_file(self, path):
        self.file_paths.remove(path)
        self.refresh_file_list()
        self.export_button.setEnabled(bool(self.file_paths))

        if path.endswith(".xlsx"):
            self.table.clearContents()
            self.table.setRowCount(0)

    def display_excel(self, file_path):
        try:
            df = pd.read_excel(file_path)
            self.table.setRowCount(len(df))
            self.table.setColumnCount(len(df.columns))
            self.table.setHorizontalHeaderLabels(df.columns)

            for i in range(len(df)):
                for j in range(len(df.columns)):
                    val = str(df.iloc[i, j])
                    item = QTableWidgetItem(val)
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                    self.table.setItem(i, j, item)

        except Exception as e:
            print(f"Error loading Excel: {e}")


    def export_fmw(self):
        try:
            excel_path = next((f for f in self.file_paths if f.endswith(".xlsx")), None)
            if not excel_path:
                print("❌ No Excel file found.")
                return

            template_path = os.path.join(os.getcwd(), "templates", "AutoTest Program.fmw")
  # <- Replace with your real path
            output_dir = os.path.dirname(excel_path)

            new_file = generate_fmw_from_template(excel_path, template_path, output_dir)
            self.title.setText(f"✅ Exported: {os.path.basename(new_file)}")

            toast = Toast("✅ Program exported as .fmw file!", self)
            toast.show_(self.mapToGlobal(self.rect().bottomRight()).x(),
                        self.mapToGlobal(self.rect().bottomRight()).y())

            # Open output folder
            if platform.system() == "Darwin":
                subprocess.call(["open", output_dir])
            elif platform.system() == "Windows":
                subprocess.call(["explorer", os.path.abspath(output_dir)])
            elif platform.system() == "Linux":
                subprocess.call(["xdg-open", output_dir])

        except Exception as e:
            print("❌ Export failed:", e)
