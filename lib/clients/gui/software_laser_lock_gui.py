import sys
from PyQt4 import QtGui, QtCore

from common.lib.clients.qtui.q_custom_text_changing_button import \
    TextChangingButton as _TextChangingButton


class TextChangingButton(_TextChangingButton):
    def __init__(self, button_text=None, parent=None):
        super(TextChangingButton, self).__init__(button_text, parent)
        self.setMaximumHeight(30)


class software_laser_lock_channel(QtGui.QFrame):
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

        self.wavelength = QtGui.QLabel('frequency')
        self.wavelength.setFont(QtGui.QFont(shell_font,pointSize=70))
        self.wavelength.setAlignment(QtCore.Qt.AlignCenter)
        self.wavelength.setStyleSheet('color: blue')

        # Create lock button
        self.lockSwitch = TextChangingButton(('Locked','Unlocked'))


        #frequency switch label
        lockName = QtGui.QLabel('Lock Frequency')
        lockName.setFont(QtGui.QFont(shell_font, pointSize=16))
        lockName.setAlignment(QtCore.Qt.AlignCenter)

        # frequency
        self.spinFreq1 = QtGui.QDoubleSpinBox()
        self.spinFreq1.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinFreq1.setDecimals(6)
        self.spinFreq1.setSingleStep(1e-6)
        self.spinFreq1.setRange(0, 1e4)
        self.spinFreq1.setKeyboardTracking(False)

        #exposure label
        exposureName = QtGui.QLabel('Exposure')
        exposureName.setFont(QtGui.QFont(shell_font, pointSize=16))
        exposureName.setAlignment(QtCore.Qt.AlignCenter)

        # exposure
        self.spinExposure = QtGui.QDoubleSpinBox()
        self.spinExposure.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinExposure.setDecimals(0)
        self.spinExposure.setSingleStep(1)
        self.spinExposure.setRange(0, 2000)
        self.spinExposure.setKeyboardTracking(False)

        #gain  label
        gainName = QtGui.QLabel('Gain')
        gainName.setFont(QtGui.QFont(shell_font, pointSize=16))
        gainName.setAlignment(QtCore.Qt.AlignCenter)

        # gain
        self.spinGain = QtGui.QDoubleSpinBox()
        self.spinGain.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinGain.setDecimals(3)
        self.spinGain.setSingleStep(1e-3)
        self.spinGain.setRange(1e-3, 1)
        self.spinGain.setKeyboardTracking(False)

        #rails  label
        lowRail = QtGui.QLabel('Low Rail')
        lowRail.setFont(QtGui.QFont(shell_font, pointSize=16))
        lowRail.setAlignment(QtCore.Qt.AlignCenter)


        # low rail
        self.spinLowRail = QtGui.QDoubleSpinBox()
        self.spinLowRail.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinLowRail.setDecimals(0)
        self.spinLowRail.setSingleStep(1)
        self.spinLowRail.setRange(0 , 50)
        self.spinLowRail.setKeyboardTracking(False)

        #high rails  label
        highRail = QtGui.QLabel('High Rail')
        highRail.setFont(QtGui.QFont(shell_font, pointSize=16))
        highRail.setAlignment(QtCore.Qt.AlignCenter)


        # high rail
        self.spinHighRail = QtGui.QDoubleSpinBox()
        self.spinHighRail.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinHighRail.setDecimals(0)
        self.spinHighRail.setSingleStep(1)
        self.spinHighRail.setRange(0 , 50)
        self.spinHighRail.setKeyboardTracking(False)

       # Too lazy to add signals to the server so
        # will update and display dac voltage every time
        # frequency updates
        self.dacLabel = QtGui.QLabel('Dac Voltage')
        self.dacLabel.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=30))
        self.dacLabel.setAlignment(QtCore.Qt.AlignCenter)


        self.dacVoltage = QtGui.QLabel('0.0')
        self.dacVoltage.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=30))
        self.dacVoltage.setAlignment(QtCore.Qt.AlignCenter)


        # clear lock button for voltage stuck too high
        self.clear_lock = QtGui.QPushButton('Clear Lock Voltage')
        self.clear_lock.setMaximumHeight(30)
        self.clear_lock.setFont(QtGui.QFont('MS Shell Dlg 2', pointSize=12))



        layout.addWidget(chanName, 1,1)
        layout.addWidget(self.wavelength, 2,0, 6, 2)
        layout.addWidget(self.lockSwitch, 1, 3, 1, 1)
        layout.addWidget(lockName, 8, 0, 1, 1)
        layout.addWidget(self.spinFreq1, 9, 0, 1, 1)
        layout.addWidget(exposureName, 8, 1, 1, 1)
        layout.addWidget(self.spinExposure, 9, 1, 1, 1)
        layout.addWidget(gainName, 2, 3, 1, 1)
        layout.addWidget(self.spinGain, 3, 3, 1, 1)
        layout.addWidget(lowRail, 4, 3, 1, 1)
        layout.addWidget(self.spinLowRail, 5, 3, 1, 1)
        layout.addWidget(highRail, 6, 3, 1, 1)
        layout.addWidget(self.spinHighRail, 7, 3, 1, 1)
        layout.addWidget(self.dacLabel, 8,3, 1, 1)
        layout.addWidget(self.dacVoltage, 9,3, 1, 1)
        layout.addWidget(self.clear_lock, 1, 0, 1, 1)

        layout.minimumSize()

        self.setLayout(layout)



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    icon = software_laser_lock_channel('cooling laser')
    icon.show()
    app.exec_()
