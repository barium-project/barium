# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 18:14:56 2020

@author: barium133
"""

import sys
from PyQt4 import QtGui, QtCore
from common.lib.clients.qtui.q_custom_text_changing_button import \
    TextChangingButton


class StretchedLabel(QtGui.QLabel):
    def __init__(self, *args, **kwargs):
        QtGui.QLabel.__init__(self, *args, **kwargs)
        self.setMinimumSize(QtCore.QSize(500, 300))

    def resizeEvent(self, evt):

        font = self.font()
        font.setPixelSize(self.width() * 0.14 - 14)
        self.setFont(font)


class QCustomFiberSwitchGui(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setFrameStyle(0x0001 | 0x0030)
        self.makeLayout()

    def makeLayout(self):
        layout = QtGui.QGridLayout()

        shell_font = 'MS Shell Dlg 2'
        title = QtGui.QLabel('Optical Fiber Switch')
        title.setFont(QtGui.QFont(shell_font, pointSize=16))
        title.setAlignment(QtCore.Qt.AlignCenter)

        switchChannels = QtGui.QLabel('Switch Channels to: ')
        switchChannels.setFont(QtGui.QFont(shell_font, pointSize=16))
        switchChannels.setAlignment(QtCore.Qt.AlignCenter)

        self.c1 = QtGui.QPushButton("1", self)
        self.c1.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c1label =  QtGui.QLabel()
        self.c1label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c1label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.c2 = QtGui.QPushButton("2", self)
        self.c2.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c2label =  QtGui.QLabel()
        self.c2label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c2label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.c3 = QtGui.QPushButton("3", self)
        self.c3.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c3label =  QtGui.QLabel()
        self.c3label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c3label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.c4 = QtGui.QPushButton("4", self)
        self.c4.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c4label =  QtGui.QLabel()
        self.c4label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c4label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.c5 = QtGui.QPushButton("5", self)
        self.c5.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c5label =  QtGui.QLabel()
        self.c5label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c5label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.c6 = QtGui.QPushButton("6", self)
        self.c6.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c6label =  QtGui.QLabel()
        self.c6label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c6label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.c7 = QtGui.QPushButton("7", self)
        self.c7.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c7label =  QtGui.QLabel()
        self.c7label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c7label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.c8 = QtGui.QPushButton("8", self)
        self.c8.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c8label =  QtGui.QLabel()
        self.c8label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c8label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.checkChannel = QtGui.QPushButton("Check Current Channel", self)
        self.checkChannel.setFont(QtGui.QFont(shell_font, pointSize=16))
        
        self.displayChannel = QtGui.QLabel('0') #not sure if this is how u do it
        self.displayChannel.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.displayChannel.setAlignment(QtCore.Qt.AlignCenter)

        #layout 1 row at a time

        layout.addWidget(title,                    0, 2, 1, 4)

        layout.addWidget(switchChannels,           1, 0, 1, 4)

        layout.addWidget(self.c1,                  2, 0, 1, 1)
        layout.addWidget(self.c2,                  2, 1, 1, 1)
        layout.addWidget(self.c3,                  2, 2, 1, 1)
        layout.addWidget(self.c4,                  2, 3, 1, 1)

        layout.addWidget(self.c5,                  4, 0, 1, 1)
        layout.addWidget(self.c6,                  4, 1, 1, 1)
        layout.addWidget(self.c7,                  4, 2, 1, 1)
        layout.addWidget(self.c8,                  4, 3, 1, 1)

        layout.addWidget(self.checkChannel,        2, 5, 1, 2)
        layout.addWidget(self.displayChannel,      3, 5, 1, 2)
        
        layout.addWidget(self.c1label,                  3, 0, 1, 1)
        layout.addWidget(self.c2label,                  3, 1, 1, 1)
        layout.addWidget(self.c3label,                  3, 2, 1, 1)
        layout.addWidget(self.c4label,                  3, 3, 1, 1)

        layout.addWidget(self.c5label,                  5, 0, 1, 1)
        layout.addWidget(self.c6label,                  5, 1, 1, 1)
        layout.addWidget(self.c7label,                  5, 2, 1, 1)
        layout.addWidget(self.c8label,                  5, 3, 1, 1)


        layout.minimumSize()

        self.setLayout(layout)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    icon = QCustomFiberSwitchGui()
    icon.show()
    app.exec_()

