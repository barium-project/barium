import sys
from PyQt4 import QtGui, QtCore
from common.lib.clients.qtui.q_custom_text_changing_button import \
    TextChangingButton


class StretchedLabel(QtGui.QLabel):
    def __init__(self, *args, **kwargs):
        QtGui.QLabel.__init__(self, *args, **kwargs)
        self.setMinimumSize(QtCore.QSize(350, 100))

    def resizeEvent(self, evt):

        font = self.font()
        font.setPixelSize(self.width() * 0.14 - 14)
        self.setFont(font)


class QCustomARampGui(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setFrameStyle(0x0001 | 0x0030)
        self.makeLayout()

    def makeLayout(self):
        layout = QtGui.QGridLayout()

        shell_font = 'MS Shell Dlg 2'
        title = QtGui.QLabel('A-Ramp')
        title.setFont(QtGui.QFont(shell_font, pointSize=16))
        title.setAlignment(QtCore.Qt.AlignCenter)

        waitTime = QtGui.QLabel('Wait Time')
        waitTime.setFont(QtGui.QFont(shell_font, pointSize=16))
        waitTime.setAlignment(QtCore.Qt.AlignCenter)

        Time = QtGui.QLabel('(S)')
        Time.setFont(QtGui.QFont(shell_font, pointSize=16))
        Time.setAlignment(QtCore.Qt.AlignCenter)

        dcName = QtGui.QLabel('DC (V)')
        dcName.setFont(QtGui.QFont(shell_font, pointSize=16))
        dcName.setAlignment(QtCore.Qt.AlignCenter)

        rod1Name = QtGui.QLabel('Rod 1')
        rod1Name.setFont(QtGui.QFont(shell_font, pointSize=16))
        rod1Name.setAlignment(QtCore.Qt.AlignCenter)

        rod2Name = QtGui.QLabel('Rod 2')
        rod2Name.setFont(QtGui.QFont(shell_font, pointSize=16))
        rod2Name.setAlignment(QtCore.Qt.AlignCenter)

        rod3Name = QtGui.QLabel('Rod 3')
        rod3Name.setFont(QtGui.QFont(shell_font, pointSize=16))
        rod3Name.setAlignment(QtCore.Qt.AlignCenter)

        rod4Name = QtGui.QLabel('Rod 4')
        rod4Name.setFont(QtGui.QFont(shell_font, pointSize=16))
        rod4Name.setAlignment(QtCore.Qt.AlignCenter)


        self.waitTime = QtGui.QDoubleSpinBox()
        self.waitTime.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.waitTime.setDecimals(1)
        self.waitTime.setSingleStep(.1)
        self.waitTime.setRange(0, 26.5)
        self.waitTime.setKeyboardTracking(False)


        # DC
        self.spinDC1 = QtGui.QDoubleSpinBox()
        self.spinDC1.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinDC1.setDecimals(4)
        self.spinDC1.setSingleStep(.01)
        self.spinDC1.setRange(0, 10)
        self.spinDC1.setKeyboardTracking(False)

        self.spinDC2 = QtGui.QDoubleSpinBox()
        self.spinDC2.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinDC2.setDecimals(4)
        self.spinDC2.setSingleStep(.01)
        self.spinDC2.setRange(0, 10)
        self.spinDC2.setKeyboardTracking(False)

        self.spinDC3 = QtGui.QDoubleSpinBox()
        self.spinDC3.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinDC3.setDecimals(4)
        self.spinDC3.setSingleStep(.01)
        self.spinDC3.setRange(0, 10)
        self.spinDC3.setKeyboardTracking(False)

        self.spinDC4 = QtGui.QDoubleSpinBox()
        self.spinDC4.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinDC4.setDecimals(4)
        self.spinDC4.setSingleStep(.01)
        self.spinDC4.setRange(0, 10)
        self.spinDC4.setKeyboardTracking(False)


        self.ARamp = QtGui.QPushButton('A-Ramp')
        self.ARamp.setMaximumHeight(30)
        self.ARamp.setMinimumHeight(30)
        self.ARamp.setFont(QtGui.QFont(shell_font, pointSize=14))
        self.ARamp.setStyleSheet("background-color: green")


        #layout 1 row at a time

        layout.addWidget(title,                    0, 0, 1, 4)

        layout.addWidget(dcName,                   1, 2, 1, 2)

        layout.addWidget(rod1Name,                 2, 0, 1, 2)
        layout.addWidget(self.spinDC1,             2, 2, 1, 2)

        layout.addWidget(rod2Name,                 3, 0, 1, 2)
        layout.addWidget(self.spinDC2,             3, 2, 1, 2)

        layout.addWidget(rod3Name,                 4, 0, 1, 2)
        layout.addWidget(self.spinDC3,             4, 2, 1, 2)

        layout.addWidget(rod4Name,                 5, 0, 1, 2)
        layout.addWidget(self.spinDC4,             5, 2, 1, 2)

        layout.addWidget(Time,                     6, 2, 1, 2)

        layout.addWidget(waitTime,                 7, 0, 1, 2)
        layout.addWidget(self.waitTime,            7, 2, 1, 2)

        layout.addWidget(self.ARamp,               8, 0, 1, 4)

        layout.minimumSize()

        self.setLayout(layout)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    icon = QCustomARampGui()
    icon.show()
    app.exec_()
