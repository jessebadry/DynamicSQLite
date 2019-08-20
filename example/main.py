import sys

from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot

import DatabaseModelWrapper as db
import models
from PyQt5.QtWidgets import *


class DynamicTable(QTableWidget):
    LoadRecords = pyqtSignal(list)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__()
        self.setParent(parent)
        self.records = []

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        self.LoadRecords.connect(self.load_persons)

    def replace(self, condition, model):
        row = int(model['id'])

        for i, key in enumerate(model.keys()):
            self.setItem(row, i, QTableWidgetItem(model[key]))

    def get_current(self):

        return self.records[self.currentIndex().row()]

    def addModel(self, model):
        row = self.rowCount()

        for index, key in enumerate(model.getKeys()):
            self.setItem(row, index, QTableWidgetItem(model.data[key]))

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Enter - 1:
            print('')

        super(DynamicTable, self).keyPressEvent(event)

    @pyqtSlot(list)
    def load_persons(self, persons):

        self.records = persons

        if len(self.records) != 0:

            columns = self.records[0].get_columns()
            col_count = len(columns)

            self.setColumnCount(col_count)

            self.setRowCount(len(self.records))
            self.setHorizontalHeaderLabels(columns)
            for i in range(self.rowCount()):
                vals = self.records[i].get_vals()

                for j in range(self.columnCount()):
                    val = vals[j]
                    item = QTableWidgetItem(str(val))
                    self.setItem(i, j, item)

            self.resizeRowsToContents()
            self.resizeColumnsToContents()
            self.setWordWrap(True)


        else:
            self.setColumnCount(0)
            self.setRowCount(0)


def main():
    app = QApplication(sys.argv)
    mainWidget = QWidget()
    layout = QVBoxLayout()
    mainWidget.setLayout(layout)

    invoices = db.get_invoices(1000)
    table = DynamicTable(mainWidget)

    table.LoadRecords.emit(invoices)
    layout.addWidget(table)
    mainWidget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
