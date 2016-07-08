# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\barium133\Code\barium\lib\clients\gui\CommandLine_gui.ui'
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

class CommandLine_UI(QtGui.QWidget):
    def setupUi(self):
        Form = self
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(400, 150)
        self.frame = QtGui.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(9, 9, 381, 131))
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(10, 10, 241, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.cl_command_text = QtGui.QPlainTextEdit(self.frame)
        self.cl_command_text.setGeometry(QtCore.QRect(10, 40, 361, 81))
        self.cl_command_text.setObjectName(_fromUtf8("cl_command_text"))
        self.cl_command_button = QtGui.QPushButton(self.frame)
        self.cl_command_button.setGeometry(QtCore.QRect(214, 10, 151, 23))
        self.cl_command_button.setObjectName(_fromUtf8("cl_command_button"))

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self):
        Form = self
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label.setText(_translate("Form", "Command Line (Python)", None))
        self.cl_command_text.setToolTip(_translate("Form", "cl_command_text", None))
        self.cl_command_button.setToolTip(_translate("Form", "cl_command_button", None))
        self.cl_command_button.setText(_translate("Form", "Send Command", None))

