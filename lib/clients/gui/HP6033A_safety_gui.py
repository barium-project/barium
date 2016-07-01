# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Barium133\Code\barium\lib\clients\gui\HP6033A_safety_gui.ui'
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

class HP6033A_Safety_UI(QtGui.QWidget):
    def setupUi(self):
        Form = self
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(400, 150)
        self.frame = QtGui.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(10, 10, 381, 131))
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(10, 6, 361, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.ps_max_voltage_spinbox = QtGui.QDoubleSpinBox(self.frame)
        self.ps_max_voltage_spinbox.setGeometry(QtCore.QRect(100, 40, 81, 31))
        self.ps_max_voltage_spinbox.setMaximum(20.0)
        self.ps_max_voltage_spinbox.setProperty("value", 20.0)
        self.ps_max_voltage_spinbox.setObjectName(_fromUtf8("ps_max_voltage_spinbox"))
        self.ps_min_voltage_spinbox = QtGui.QDoubleSpinBox(self.frame)
        self.ps_min_voltage_spinbox.setGeometry(QtCore.QRect(100, 81, 81, 31))
        self.ps_min_voltage_spinbox.setMaximum(20.0)
        self.ps_min_voltage_spinbox.setObjectName(_fromUtf8("ps_min_voltage_spinbox"))
        self.ps_max_current_spinbox = QtGui.QDoubleSpinBox(self.frame)
        self.ps_max_current_spinbox.setGeometry(QtCore.QRect(290, 40, 81, 31))
        self.ps_max_current_spinbox.setMaximum(30.0)
        self.ps_max_current_spinbox.setProperty("value", 30.0)
        self.ps_max_current_spinbox.setObjectName(_fromUtf8("ps_max_current_spinbox"))
        self.ps_min_current_spinbox = QtGui.QDoubleSpinBox(self.frame)
        self.ps_min_current_spinbox.setGeometry(QtCore.QRect(290, 81, 81, 31))
        self.ps_min_current_spinbox.setMaximum(30.0)
        self.ps_min_current_spinbox.setObjectName(_fromUtf8("ps_min_current_spinbox"))
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 91, 31))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(10, 82, 91, 31))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(self.frame)
        self.label_4.setGeometry(QtCore.QRect(210, 44, 81, 21))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(self.frame)
        self.label_5.setGeometry(QtCore.QRect(210, 80, 81, 31))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.line = QtGui.QFrame(self.frame)
        self.line.setGeometry(QtCore.QRect(179, 40, 31, 81))
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self):
        Form = self
        Form.setWindowTitle(_translate("Form", "Power Supply Safety Limits", None))
        self.label.setText(_translate("Form", "Power Supply Safety Limits", None))
        self.label_2.setText(_translate("Form", "Max Voltage:", None))
        self.label_3.setText(_translate("Form", "Min Voltage:", None))
        self.label_4.setText(_translate("Form", "Max Current:", None))
        self.label_5.setText(_translate("Form", "Min Current:", None))

