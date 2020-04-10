from PyQt5 import uic, QtWidgets, QtCore, Qt, QtGui
from PyQt5.QtWidgets import (QApplication, QDialog, QPushButton, QTableWidget,
                             QTableWidgetItem, QAbstractItemView, QHeaderView, QMenu,
                             QActionGroup, QAction, QMessageBox, QInputDialog, QWidget,
                             QFileDialog)

from PyQt5.QtGui import QPainter, QColor, QFont
import numpy.core._methods
import numpy.lib.format
import numpy as np
import shutil
import sys
import os

from autocomplete import AutoComplete

qtCreatorFile = "gui.ui" # Nombre del archivo aquí.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    icons_path = "" 
    def __init__(self, parent = None):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("AutoComplete")

        #Oración
        self.oracion = str()
        self.list_words = list()
        self.space = 0
        self.AutoWord = str()

        #Botones
        self.aBtn.clicked.connect(lambda event: self.abcClick(1))
        self.bBtn.clicked.connect(lambda event: self.abcClick(2))
        self.cBtn.clicked.connect(lambda event: self.abcClick(3))
        self.dBtn.clicked.connect(lambda event: self.abcClick(4))
        self.eBtn.clicked.connect(lambda event: self.abcClick(5))
        self.fBtn.clicked.connect(lambda event: self.abcClick(6))
        self.gBtn.clicked.connect(lambda event: self.abcClick(7))
        self.hBtn.clicked.connect(lambda event: self.abcClick(8))
        self.iBtn.clicked.connect(lambda event: self.abcClick(9))
        self.jBtn.clicked.connect(lambda event: self.abcClick(10))
        self.kBtn.clicked.connect(lambda event: self.abcClick(11))
        self.lBtn.clicked.connect(lambda event: self.abcClick(12))
        self.mBtn.clicked.connect(lambda event: self.abcClick(13))
        self.nBtn.clicked.connect(lambda event: self.abcClick(14))
        self.nnBtn.clicked.connect(lambda event: self.abcClick(15))
        self.oBtn.clicked.connect(lambda event: self.abcClick(16))
        self.pBtn.clicked.connect(lambda event: self.abcClick(17))
        self.qBtn.clicked.connect(lambda event: self.abcClick(18))
        self.rBtn.clicked.connect(lambda event: self.abcClick(19))
        self.sBtn.clicked.connect(lambda event: self.abcClick(20))
        self.tBtn.clicked.connect(lambda event: self.abcClick(21))
        self.uBtn.clicked.connect(lambda event: self.abcClick(22))
        self.vBtn.clicked.connect(lambda event: self.abcClick(23))
        self.wBtn.clicked.connect(lambda event: self.abcClick(24))
        self.xBtn.clicked.connect(lambda event: self.abcClick(25))
        self.yBtn.clicked.connect(lambda event: self.abcClick(26))
        self.zBtn.clicked.connect(lambda event: self.abcClick(27))
        self.spaceBtn.clicked.connect(lambda event: self.abcClick(28))
        self.delBtn.clicked.connect(lambda event: self.abcClick(29))

        self.newBtn.clicked.connect(self.newSentence)


    def abcClick(self, number):
        '''
        Que letra se presionó
        '''
        abc = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'ñ', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', ' ']
        autocomplete = AutoComplete()
        if not number>28:
            self.oracion += abc[number-1]
            self.list_words = self.oracion.split(" ")
            self.AutoWord = self.list_words[-1]
            print(self.list_words, self.AutoWord)
            
        else:
            if number==29: #borrar
                self.oracion = self.oracion[:-1]
                self.list_words = self.oracion.split(" ")
                self.AutoWord = self.list_words[-1]
                print(self.list_words, self.AutoWord)

        self.plainTextEdit.clear()
        self.plainTextEdit.insertPlainText(self.oracion)
        #Buscar opciones para completar
        autocomplete = AutoComplete()
        words = autocomplete.showOptions(self.AutoWord)
        self.word.setText(self.AutoWord)
        opciones = list()
        opsBtn = [self.op1, self.op2, self.op3]
        for i, option in enumerate(words):
            opciones.append(option)
            opsBtn[i].setText(opciones[i])#Mostrar las opciones
    
    def newSentence(self):
        print("Guardar oración")
        self.plainTextEdit.clear()
        autocomplete = AutoComplete()
        for palabra in self.list_words:
            autocomplete.saveSentence(palabra)
        self.oracion = str()


if __name__ == "__main__":
    app =  QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
