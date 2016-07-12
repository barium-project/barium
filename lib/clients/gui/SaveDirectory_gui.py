# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\barium133\Code\barium\lib\clients\gui\SaveDirectory_gui.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class SaveDirectory_UI(QtGui.QWidget):
    def setupUi(self):
        Form = self
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(400, 150)
        self.frame = QtGui.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(10, 10, 381, 131))
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.label_24 = QtGui.QLabel(self.frame)
        self.label_24.setGeometry(QtCore.QRect(10, 100, 51, 20))
        self.label_24.setObjectName(_fromUtf8("label_24"))
        self.sd_filename_text = QtGui.QLineEdit(self.frame)
        self.sd_filename_text.setGeometry(QtCore.QRect(60, 100, 311, 20))
        self.sd_filename_text.setObjectName(_fromUtf8("sd_filename_text"))
        self.label_23 = QtGui.QLabel(self.frame)
        self.label_23.setGeometry(QtCore.QRect(10, 50, 71, 16))
        self.label_23.setObjectName(_fromUtf8("label_23"))
        self.sd_save_path_select = QtGui.QComboBox(self.frame)
        self.sd_save_path_select.setGeometry(QtCore.QRect(10, 70, 361, 21))
        self.sd_save_path_select.setEditable(True)
        self.sd_save_path_select.setObjectName(_fromUtf8("sd_save_path_select"))
        self.sd_save_path_select.addItem(_fromUtf8(""))
        self.sd_save_path_select.addItem(_fromUtf8(""))
        self.label = QtGui.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(10, 16, 221, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.sd_select_path_button = QtGui.QPushButton(self.frame)
        self.sd_select_path_button.setGeometry(QtCore.QRect(250, 50, 121, 21))
        self.sd_select_path_button.setObjectName(_fromUtf8("sd_select_path_button"))

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self):
        Form = self
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label_24.setText(_translate("Form", "File Name", None))
        self.sd_filename_text.setToolTip(_translate("Form", "<html><head/><body><p>Name of saved data file</p></body></html>", None))
        self.sd_filename_text.setText(_translate("Form", "data.txt", None))
        self.label_23.setText(_translate("Form", "Save File Path", None))
        self.sd_save_path_select.setToolTip(_translate("Form", "<html><head/><body><p>Path to save directory</p></body></html>", None))
        self.sd_save_path_select.setItemText(0, _translate("Form", "Z:\\Group_Share\\Barium\\Data\\", None))
        self.sd_save_path_select.setItemText(1, _translate("Form", "C:\\Users\\barium133\\Desktop\\", None))
        self.label.setText(_translate("Form", "Save Directory", None))
        self.sd_select_path_button.setText(_translate("Form", "Select Path ...", None))

