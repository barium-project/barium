# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\barium133\Code\barium\lib\clients\gui\Timers_gui.ui'
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

class Timers_UI(QtGui.QWidget):
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
        self.label.setGeometry(QtCore.QRect(10, 10, 121, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.t_right_lcd = QtGui.QLCDNumber(self.frame)
        self.t_right_lcd.setGeometry(QtCore.QRect(260, 90, 111, 31))
        self.t_right_lcd.setObjectName(_fromUtf8("t_right_lcd"))
        self.t_middle_lcd = QtGui.QLCDNumber(self.frame)
        self.t_middle_lcd.setGeometry(QtCore.QRect(140, 90, 111, 31))
        self.t_middle_lcd.setObjectName(_fromUtf8("t_middle_lcd"))
        self.t_left_lcd = QtGui.QLCDNumber(self.frame)
        self.t_left_lcd.setGeometry(QtCore.QRect(20, 90, 111, 31))
        self.t_left_lcd.setObjectName(_fromUtf8("t_left_lcd"))
        self.t_left_label = QtGui.QLabel(self.frame)
        self.t_left_label.setGeometry(QtCore.QRect(20, 70, 111, 21))
        self.t_left_label.setObjectName(_fromUtf8("t_left_label"))
        self.t_middle_label = QtGui.QLabel(self.frame)
        self.t_middle_label.setGeometry(QtCore.QRect(140, 72, 111, 21))
        self.t_middle_label.setObjectName(_fromUtf8("t_middle_label"))
        self.t_right_label = QtGui.QLabel(self.frame)
        self.t_right_label.setGeometry(QtCore.QRect(260, 72, 111, 21))
        self.t_right_label.setObjectName(_fromUtf8("t_right_label"))
        self.t_right_button = QtGui.QPushButton(self.frame)
        self.t_right_button.setGeometry(QtCore.QRect(260, 20, 111, 41))
        self.t_right_button.setObjectName(_fromUtf8("t_right_button"))
        self.t_middle_button = QtGui.QPushButton(self.frame)
        self.t_middle_button.setGeometry(QtCore.QRect(140, 20, 111, 41))
        self.t_middle_button.setObjectName(_fromUtf8("t_middle_button"))
        self.t_spinbox = QtGui.QDoubleSpinBox(self.frame)
        self.t_spinbox.setGeometry(QtCore.QRect(20, 40, 111, 22))
        self.t_spinbox.setObjectName(_fromUtf8("t_spinbox"))

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self):
        Form = self
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label.setText(_translate("Form", "Timers", None))
        self.t_left_label.setText(_translate("Form", "LeftTimer", None))
        self.t_middle_label.setText(_translate("Form", "MiddleTimer", None))
        self.t_right_label.setText(_translate("Form", "RightTimer", None))
        self.t_right_button.setText(_translate("Form", "RightButton", None))
        self.t_middle_button.setText(_translate("Form", "MiddleButton", None))

