# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\barium133\Code\barium\lib\clients\gui\LabRADconnection_gui.ui'
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

class LabRADconnection_UI(QtGui.QWidget):
    def setupUi(self):
        Form = self
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(1200, 140)
        self.frame = QtGui.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(10, 10, 1181, 121))
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(10, 10, 171, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.autoconnect_button = QtGui.QPushButton(self.frame)
        self.autoconnect_button.setGeometry(QtCore.QRect(420, 40, 371, 71))
        self.autoconnect_button.setCheckable(False)
        self.autoconnect_button.setObjectName(_fromUtf8("autoconnect_button"))
        self.frame_2 = QtGui.QFrame(self.frame)
        self.frame_2.setGeometry(QtCore.QRect(10, 40, 401, 71))
        self.frame_2.setFrameShape(QtGui.QFrame.Panel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.label_2 = QtGui.QLabel(self.frame_2)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 171, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(self.frame_2)
        self.label_3.setGeometry(QtCore.QRect(10, 10, 151, 21))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.host_name_text = QtGui.QComboBox(self.frame_2)
        self.host_name_text.setGeometry(QtCore.QRect(180, 10, 211, 22))
        self.host_name_text.setEditable(True)
        self.host_name_text.setObjectName(_fromUtf8("host_name_text"))
        self.host_name_text.addItem(_fromUtf8(""))
        self.host_name_text.addItem(_fromUtf8(""))
        self.host_name_text.addItem(_fromUtf8(""))
        self.host_name_text.addItem(_fromUtf8(""))
        self.lc_power_supply_id_spinbox = QtGui.QSpinBox(self.frame_2)
        self.lc_power_supply_id_spinbox.setGeometry(QtCore.QRect(180, 40, 42, 22))
        self.lc_power_supply_id_spinbox.setToolTip(_fromUtf8(""))
        self.lc_power_supply_id_spinbox.setObjectName(_fromUtf8("lc_power_supply_id_spinbox"))
        self.lc_scalar_id_spinbox = QtGui.QSpinBox(self.frame_2)
        self.lc_scalar_id_spinbox.setGeometry(QtCore.QRect(350, 40, 42, 22))
        self.lc_scalar_id_spinbox.setObjectName(_fromUtf8("lc_scalar_id_spinbox"))
        self.label_4 = QtGui.QLabel(self.frame_2)
        self.label_4.setGeometry(QtCore.QRect(230, 40, 121, 21))
        self.label_4.setObjectName(_fromUtf8("label_4"))

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self):
        Form = self
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label.setText(_translate("Form", "LabRAD Connection", None))
        self.autoconnect_button.setText(_translate("Form", "Connect to LabRAD and run Clients (HP6033A, SR430 Scalar, and RGA)", None))
        self.label_2.setToolTip(_translate("Form", "Leave at 0 if only one HP6033A device connected.", None))
        self.label_2.setText(_translate("Form", "HP6033A Power Supply Device ID:", None))
        self.label_3.setText(_translate("Form", "Host Name", None))
        self.host_name_text.setItemText(0, _translate("Form", "PlanetExpress", None))
        self.host_name_text.setItemText(1, _translate("Form", "bender", None))
        self.host_name_text.setItemText(2, _translate("Form", "flexo", None))
        self.host_name_text.setItemText(3, _translate("Form", "calculon", None))
        self.label_4.setToolTip(_translate("Form", "Leave at 0 if only one SR430 device connected.", None))
        self.label_4.setText(_translate("Form", "SR430 Scalar Device ID:", None))

