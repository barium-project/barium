# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\barium133\Code\barium\lib\clients\gui\DataLog_gui.ui'
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

class DataLog_UI(QtGui.QWidget):
    def setupUi(self):
        Form = self
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(800, 600)
        self.frame = QtGui.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(10, 10, 781, 581))
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(10, 10, 261, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.ms_data_text = QtGui.QPlainTextEdit(self.frame)
        self.ms_data_text.setGeometry(QtCore.QRect(10, 40, 761, 531))
        self.ms_data_text.setReadOnly(True)
        self.ms_data_text.setOverwriteMode(False)
        self.ms_data_text.setObjectName(_fromUtf8("ms_data_text"))

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self):
        Form = self
        Form.setWindowTitle(_translate("Form", "Data Log", None))
        self.label.setText(_translate("Form", "Data Log", None))

