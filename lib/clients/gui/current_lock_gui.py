import sys
from PyQt4 import QtGui, QtCore

from common.lib.clients.qtui.q_custom_text_changing_button import \
    TextChangingButton as _TextChangingButton


class TextChangingButton(_TextChangingButton):
    def __init__(self, button_text=None, parent=None):
        super(TextChangingButton, self).__init__(button_text, parent)
        self.setMaximumHeight(30)


class current_lock_gui(QtGui.QFrame):
    def __init__(self, chanName,  parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.setFrameStyle(0x0001 | 0x0030)
        self.makeLayout(chanName)

    def makeLayout(self, name):
        layout = QtGui.QGridLayout()


        shell_font = 'MS Shell Dlg 2'
        chanName = QtGui.QLabel(name)
        chanName.setFont(QtGui.QFont(shell_font, pointSize=16))
        chanName.setAlignment(QtCore.Qt.AlignCenter)

        self.current = QtGui.QLabel('current')
        self.current.setFont(QtGui.QFont(shell_font,pointSize=70))
        self.current.setAlignment(QtCore.Qt.AlignCenter)
        self.current.setStyleSheet('color: blue')

        # Create lock button
        self.lockSwitch = TextChangingButton(('Locked','Unlocked'))


        #frequency switch label
        lockName = QtGui.QLabel('Lock Current')
        lockName.setFont(QtGui.QFont(shell_font, pointSize=16))
        lockName.setAlignment(QtCore.Qt.AlignCenter)

        # frequency
        self.spinFreq1 = QtGui.QDoubleSpinBox()
        self.spinFreq1.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinFreq1.setDecimals(6)
        self.spinFreq1.setSingleStep(1e-6)
        self.spinFreq1.setRange(0, 1e4)
        self.spinFreq1.setKeyboardTracking(False)

    
        #gain  label
        gainName = QtGui.QLabel('Gain')
        gainName.setFont(QtGui.QFont(shell_font, pointSize=16))
        gainName.setAlignment(QtCore.Qt.AlignCenter)

        # gain
        self.spinGain = QtGui.QDoubleSpinBox()
        self.spinGain.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinGain.setDecimals(6)
        self.spinGain.setSingleStep(1e-6)
        self.spinGain.setRange(1e-6, 1)
        self.spinGain.setKeyboardTracking(False)



        layout.addWidget(chanName, 1,1)
        layout.addWidget(self.current, 2,0, 6, 2)
        layout.addWidget(self.lockSwitch, 1, 3, 1, 1)
        layout.addWidget(lockName, 10, 0, 1, 1)
        layout.addWidget(self.spinFreq1, 11, 0, 1, 1)
        layout.addWidget(gainName, 2, 3, 1, 1)
        layout.addWidget(self.spinGain, 3, 3, 1, 1)
        layout.minimumSize()

        self.setLayout(layout)



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    icon = current_lock('493 Injection Locked Laser')
    icon.show()
    app.exec_()
