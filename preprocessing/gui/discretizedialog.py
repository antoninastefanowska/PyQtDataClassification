from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QComboBox, QLineEdit
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIntValidator

from preprocessing.utils.namegenerator import NameGenerator
from preprocessing.columnprocessor import ColumnProcessor

class DiscretizeDialog(QDialog):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.data = data
        self.load_ui()

    def load_ui(self):
        uic.loadUi("ui/discretizedialog.ui", self)
        column_name_combobox = self.findChild(QComboBox, "columnNameCombobox")
        bar_number_textbox = self.findChild(QLineEdit, "barNumberTextbox")
        column_name_combobox.addItems(self.data.columns)
        bar_number_textbox.setValidator(QIntValidator())

    def discretize(self):
        column_name_combobox = self.findChild(QComboBox, "columnNameCombobox")
        bar_number_textbox = self.findChild(QLineEdit, "barNumberTextbox")

        column_name = column_name_combobox.currentText()
        column = self.data[column_name]
        bar_number = int(bar_number_textbox.text())

        processor = ColumnProcessor(column)
        name = NameGenerator.get_name(self.data.columns, column_name, "_dyskretne")
        self.data[name] = processor.discretize(bar_number)

    @pyqtSlot()
    def accept(self):
        self.discretize()
        super().accept()

