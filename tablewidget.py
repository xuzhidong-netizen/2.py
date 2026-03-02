import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QAbstractItemView


class TableWidget(QTableWidget):
    # class Label(QWidget,QPainter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragDropMode(QAbstractItemView.InternalMove)

    def dropEvent(self, event):
        if event.source() == self:
            rows = set([mi.row() for mi in self.selectedIndexes()])
            targetRow = self.indexAt(event.pos()).row()
            rows.discard(targetRow)
            rows = sorted(rows)
            if not rows:
                return
            if targetRow == -1:
                targetRow = self.rowCount()
            for _ in range(len(rows)):
                self.insertRow(targetRow)
                for col in range(self.columnCount()):
                    self.setSpan(targetRow, col, 1, self.columnSpan(rows[0], col))
            rowMapping = dict()  # Src row to target row.
            for idx, row in enumerate(rows):
                if row < targetRow:
                    rowMapping[row] = targetRow + idx
                else:
                    rowMapping[row + len(rows)] = targetRow + idx
            colCount = self.columnCount()
            for srcRow, tgtRow in sorted(rowMapping.items()):
                for col in range(0, colCount):
                    # print(self.item(srcRow, col))
                    if self.item(srcRow, col):
                        self.setItem(tgtRow, col, self.takeItem(srcRow, col))
                    else:
                        # 修改可以移动组件
                        self.setCellWidget(tgtRow, col, self.cellWidget(srcRow, col))
            for row in reversed(sorted(rowMapping.keys())):
                self.removeRow(row)
            event.accept()
            return

    def drop_on(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return self.rowCount()
            print("drop_on_return:", self.rowCount())

        return index.row() + 1 if self.is_below(event.pos(), index) else index.row()

    def is_below(self, pos, index):
        rect = self.visualRect(index)
        margin = 2
        if pos.y() - rect.top() < margin:
            return False
        elif rect.bottom() - pos.y() < margin:
            return True
            # noinspection PyTypeChecker
        return rect.contains(pos, True) and not (
                int(self.model().flags(index)) & Qt.ItemIsDropEnabled) and pos.y() >= rect.center().y()