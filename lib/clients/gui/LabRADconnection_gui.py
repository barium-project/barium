# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Z:\Group_Share\Barium\Users\Calvin\Dev\GUIs\LabRADconnection_gui.ui'
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
        Form.resize(1200, 120)
        self.frame = QtGui.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(10, 10, 1181, 101))
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
        self.host_ip_text = QtGui.QComboBox(self.frame)
        self.host_ip_text.setGeometry(QtCore.QRect(180, 40, 201, 22))
        self.host_ip_text.setEditable(True)
        self.host_ip_text.setObjectName(_fromUtf8("host_ip_text"))
        self.host_ip_text.addItem(_fromUtf8(""))
        self.host_ip_text.addItem(_fromUtf8(""))
        self.host_ip_text.addItem(_fromUtf8(""))
        self.host_ip_text.addItem(_fromUtf8(""))
        self.host_name_text = QtGui.QComboBox(self.frame)
        self.host_name_text.setGeometry(QtCore.QRect(180, 70, 201, 22))
        self.host_name_text.setEditable(True)
        self.host_name_text.setObjectName(_fromUtf8("host_name_text"))
        self.host_name_text.addItem(_fromUtf8(""))
        self.host_name_text.addItem(_fromUtf8(""))
        self.host_name_text.addItem(_fromUtf8(""))
        self.host_name_text.addItem(_fromUtf8(""))
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 61, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(10, 70, 151, 21))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.autoconnect_button = QtGui.QPushButton(self.frame)
        self.autoconnect_button.setGeometry(QtCore.QRect(400, 40, 371, 51))
        self.autoconnect_button.setObjectName(_fromUtf8("autoconnect_button"))

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self):
        from os import environ
        host_name = environ['LABRADNODE']
        host_name.replace(" ","_")
        Form = self
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label.setText(_translate("Form", "LabRAD Connection", None))
        self.host_ip_text.setItemText(0, _translate("Form", "127.0.0.1", None))
        self.host_ip_text.setItemText(1, _translate("Form", "10.97.111.1", None))
        self.host_ip_text.setItemText(2, _translate("Form", "10.97.111.2", None))
        self.host_ip_text.setItemText(3, _translate("Form", "10.97.111.3", None))
        self.host_name_text.setItemText(0, _translate("Form", host_name, None))
        self.host_name_text.setItemText(1, _translate("Form", "PlanetExpress", None))
        self.host_name_text.setItemText(2, _translate("Form", "bender", None))
        self.host_name_text.setItemText(3, _translate("Form", "flexo", None))
        self.label_2.setText(_translate("Form", "Host IP", None))
        self.label_3.setText(_translate("Form", "Host Name (with underscores)", None))
        self.autoconnect_button.setText(_translate("Form", "Autoconnect Everything (Clients and Servers)", None))

