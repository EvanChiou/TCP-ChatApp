from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt,pyqtSignal
import globals
import time

class myTextEdit(QtWidgets.QTextEdit):
    def __init__(self,parent):
        super().__init__(parent)
        self.parent = parent
    def keyPressEvent(self, event):
        QtWidgets.QTextEdit.keyPressEvent(self,event)
        print(globals.connected)
        if event.key() == 16777220:
            globals.EnterPressed = True
            while globals.EnterPressed and globals.connected == True:
                pass
            self.setPlainText('')
