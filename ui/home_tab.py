from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QHBoxLayout, QToolButton, QFrame, QSizePolicy, QHeaderView,
    QLineEdit, QCheckBox, QApplication, QMessageBox
)
from PyQt5.QtCore import Qt
import pandas as pd
import os
import platform
import subprocess
from toast_widget import Toast
from generate_fmw import generate_fmw_from_template


class HomeTab(QWidget):
    def __init__(self):
        super().__init__()
        self.file_paths = []

        self.title = QLabel("Recipe Editor")
        self.title.setStyleSheet("font-size: 18px; font-weight: 500; color: #f0f0f0; padding: 4px 0;")

        self.file_list_layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.DoubleClicked)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)
        self.table.setFixedHeight(220)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.setShowGrid(True)
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setDefaultSectionSize(130)

        self.load_button = QPushButton("Load Files")
        self.export_button = QPushButton("Export")
        self.save_button = QPushButton("Save")
        self.load_button.clicked.connect(self.open_file_dialog)
        self.export_button.clicked.connect(self.export_fmw)
        self.save_button.clicked.connect(self.save_excel)
        self.export_button.setEnabled(False)
        self.save_button.setEnabled(False)

        for btn in [self.load_button, self.export_button, self.save_button]:
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

        self.ref_x_input = QLineEdit("0")
        self.ref_y_input = QLineEdit("0")
        self.theta_input = QLineEdit("0")
        self.include_height_sense = QCheckBox("Include Height Sense Probe")

        ref_frame_layout = QHBoxLayout()
        ref_frame_layout.addWidget(QLabel("Ref X:"))
        ref_frame_layout.addWidget(self.ref_x_input)
        ref_frame_layout.addWidget(QLabel("Ref Y:"))
        ref_frame_layout.addWidget(self.ref_y_input)
        ref_frame_layout.addWidget(QLabel("Theta:"))
        ref_frame_layout.addWidget(self.theta_input)
        ref_frame_layout.addStretch()
        ref_frame_layout.addWidget(self.include_height_sense)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        button_row.addWidget(self.save_button)
        button_row.addStretch()
        button_row.addWidget(self.load_button)
        button_row.addWidget(self.export_button)
        button_row.addStretch()

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addLayout(self.file_list_layout)
        layout.addSpacing(10)
        layout.addWidget(self.table)
        layout.addLayout(ref_frame_layout)
        layout.addLayout(button_row)
        layout.addStretch()
        self.setLayout(layout)

    def open_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Recipe Input Files", os.getcwd(),
            "All Files (*);;Excel (*.xlsx);;Text (*.txt);;Config (*.ini)"
        )
        if files:
            self.file_paths = list(set(self.file_paths + files))
            self.export_button.setEnabled(True)
            self.save_button.setEnabled(True)
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
        self.save_button.setEnabled(bool(self.file_paths))
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

    def save_excel(self):
        excel_path = next((f for f in self.file_paths if f.endswith(".xlsx")), None)
        if not excel_path:
            print("❌ No Excel file to save.")
            return
        row_count = self.table.rowCount()
        col_count = self.table.columnCount()
        headers = [self.table.horizontalHeaderItem(i).text() for i in range(col_count)]
        data = []
        for row in range(row_count):
            row_data = []
            for col in range(col_count):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        df = pd.DataFrame(data, columns=headers)
        df.to_excel(excel_path, index=False)
        print(f"✅ Saved to {excel_path}")

    def export_fmw(self):
        try:
            from wafermap_data import _wafer_map_payload  # ✅ Make sure this import is at the top of your file
            from PyQt5.QtWidgets import QMessageBox

            # 🔔 Wafer Map Confirmation Prompt
            if not _wafer_map_payload:
                reply = QMessageBox.question(
                    self,
                    "Wafer Map Not Found",
                    "No wafer map has been submitted from the Wafer Map tab.\n\nDo you want to continue without it?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return

            excel_path = next((f for f in self.file_paths if f.endswith(".xlsx")), None)
            if not excel_path:
                print("❌ No Excel file found.")
                return

            ref_x = float(self.ref_x_input.text() or 0)
            ref_y = float(self.ref_y_input.text() or 0)
            theta = float(self.theta_input.text() or 0)
            use_height = self.include_height_sense.isChecked()

            template_path = os.path.join(os.getcwd(), "templates", "AutoTest Program.fmw")
            output_dir = os.path.join(os.getcwd(), "output")
            os.makedirs(output_dir, exist_ok=True)

            new_file = generate_fmw_from_template(
                excel_path,
                template_path,
                output_dir,
                ref_frame=(ref_x, ref_y, theta),
                include_height_sense=use_height
            )

            self.title.setText(f"✅ Exported: {os.path.basename(new_file)}")

            toast = Toast("✅ Program exported as .fmw file!", self)
            toast.show_(self.mapToGlobal(self.rect().bottomRight()).x(),
                        self.mapToGlobal(self.rect().bottomRight()).y())

            if platform.system() == "Darwin":
                subprocess.call(["open", output_dir])
            elif platform.system() == "Windows":
                subprocess.call(["explorer", os.path.abspath(output_dir)])
            elif platform.system() == "Linux":
                subprocess.call(["xdg-open", output_dir])

        except Exception as e:
            print("❌ Export failed:", e)
