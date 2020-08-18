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


class QCustomTrapGui(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setFrameStyle(0x0001 | 0x0030)
        self.makeLayout()

    def makeLayout(self):
        layout = QtGui.QGridLayout()

        shell_font = 'MS Shell Dlg 2'
        freqName = QtGui.QLabel('Frequency (Hz)')
        freqName.setFont(QtGui.QFont(shell_font, pointSize=16))
        freqName.setAlignment(QtCore.Qt.AlignCenter)

        phaseName = QtGui.QLabel('Phase (deg)')
        phaseName.setFont(QtGui.QFont(shell_font, pointSize=16))
        phaseName.setAlignment(QtCore.Qt.AlignCenter)

        ampName = QtGui.QLabel('RF Amp (V)')
        ampName.setFont(QtGui.QFont(shell_font, pointSize=16))
        ampName.setAlignment(QtCore.Qt.AlignCenter)

        dcName = QtGui.QLabel('DC (V)')
        dcName.setFont(QtGui.QFont(shell_font, pointSize=16))
        dcName.setAlignment(QtCore.Qt.AlignCenter)

        hvName = QtGui.QLabel('HV (V)')
        hvName.setFont(QtGui.QFont(shell_font, pointSize=16))
        hvName.setAlignment(QtCore.Qt.AlignCenter)

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


        endCap1Name = QtGui.QLabel('End Cap 1')
        endCap1Name.setFont(QtGui.QFont(shell_font, pointSize=16))
        endCap1Name.setAlignment(QtCore.Qt.AlignCenter)

        endCap2Name = QtGui.QLabel('End Cap 2')
        endCap2Name.setFont(QtGui.QFont(shell_font, pointSize=16))
        endCap2Name.setAlignment(QtCore.Qt.AlignCenter)

        E1Name = QtGui.QLabel('Einzel Lens 1')
        E1Name.setFont(QtGui.QFont(shell_font, pointSize=16))
        E1Name.setAlignment(QtCore.Qt.AlignCenter)

        E2Name = QtGui.QLabel('Einzel Lens 2')
        E2Name.setFont(QtGui.QFont(shell_font, pointSize=16))
        E2Name.setAlignment(QtCore.Qt.AlignCenter)


        self.update_rf = QtGui.QPushButton('Update RF')
        self.update_rf.setMaximumHeight(30)
        self.update_rf.setMinimumHeight(30)
        self.update_rf.setFont(QtGui.QFont(shell_font, pointSize=14))
        self.update_rf.setStyleSheet("background-color: green")

        self.update_dc = QtGui.QPushButton('Update DC')
        self.update_dc.setMinimumHeight(30)
        self.update_dc.setMaximumHeight(30)
        self.update_dc.setFont(QtGui.QFont(shell_font, pointSize=14))
        self.update_dc.setStyleSheet("background-color: green")

        self.clearPhase = QtGui.QPushButton('Clear Phase Accum')
        self.clearPhase.setMinimumHeight(30)
        self.clearPhase.setMaximumHeight(30)
        self.clearPhase.setFont(QtGui.QFont(shell_font, pointSize=14))
        self.clearPhase.setStyleSheet("background-color: blue")

        #self.update_dc.setMinimumWidth(180)

        #editable fields
        # frequency
        self.spinFreq1 = QtGui.QDoubleSpinBox()
        self.spinFreq1.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinFreq1.setDecimals(0)
        self.spinFreq1.setSingleStep(1)
        self.spinFreq1.setRange(0, 500e6)
        self.spinFreq1.setKeyboardTracking(False)

        self.spinFreq2 = QtGui.QDoubleSpinBox()
        self.spinFreq2.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinFreq2.setDecimals(0)
        self.spinFreq2.setSingleStep(1)
        self.spinFreq2.setRange(0, 500e6)
        self.spinFreq2.setKeyboardTracking(False)

        self.spinFreq3 = QtGui.QDoubleSpinBox()
        self.spinFreq3.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinFreq3.setDecimals(0)
        self.spinFreq3.setSingleStep(1)
        self.spinFreq3.setRange(0, 500e6)
        self.spinFreq3.setKeyboardTracking(False)

        self.spinFreq4 = QtGui.QDoubleSpinBox()
        self.spinFreq4.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinFreq4.setDecimals(0)
        self.spinFreq4.setSingleStep(1)
        self.spinFreq4.setRange(0, 500e6)
        self.spinFreq4.setKeyboardTracking(False)

        #phase
        self.spinPhase1 = QtGui.QDoubleSpinBox()
        self.spinPhase1.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinPhase1.setDecimals(1)
        self.spinPhase1.setSingleStep(.5)
        self.spinPhase1.setRange(0, 360)
        self.spinPhase1.setKeyboardTracking(False)

        self.spinPhase2 = QtGui.QDoubleSpinBox()
        self.spinPhase2.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinPhase2.setDecimals(1)
        self.spinPhase2.setSingleStep(.5)
        self.spinPhase2.setRange(0, 360)
        self.spinPhase2.setKeyboardTracking(False)

        self.spinPhase3 = QtGui.QDoubleSpinBox()
        self.spinPhase3.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinPhase3.setDecimals(1)
        self.spinPhase3.setSingleStep(.5)
        self.spinPhase3.setRange(0, 360)
        self.spinPhase3.setKeyboardTracking(False)

        self.spinPhase4 = QtGui.QDoubleSpinBox()
        self.spinPhase4.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinPhase4.setDecimals(1)
        self.spinPhase4.setSingleStep(.5)
        self.spinPhase4.setRange(0, 360)
        self.spinPhase4.setKeyboardTracking(False)


        # Amplitude
        self.spinAmp1 = QtGui.QDoubleSpinBox()
        self.spinAmp1.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinAmp1.setDecimals(0)
        self.spinAmp1.setSingleStep(1)
        self.spinAmp1.setRange(0, 1233)
        self.spinAmp1.setKeyboardTracking(False)

        self.spinAmp2 = QtGui.QDoubleSpinBox()
        self.spinAmp2.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinAmp2.setDecimals(0)
        self.spinAmp2.setSingleStep(1)
        self.spinAmp2.setRange(0, 1233)
        self.spinAmp2.setKeyboardTracking(False)

        self.spinAmp3 = QtGui.QDoubleSpinBox()
        self.spinAmp3.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinAmp3.setDecimals(0)
        self.spinAmp3.setSingleStep(1)
        self.spinAmp3.setRange(0, 1233)
        self.spinAmp3.setKeyboardTracking(False)

        self.spinAmp4 = QtGui.QDoubleSpinBox()
        self.spinAmp4.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinAmp4.setDecimals(0)
        self.spinAmp4.setSingleStep(1)
        self.spinAmp4.setRange(0, 1233)
        self.spinAmp4.setKeyboardTracking(False)

        # DC
        self.spinDC1 = QtGui.QDoubleSpinBox()
        self.spinDC1.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinDC1.setDecimals(5)
        self.spinDC1.setSingleStep(.01)
        self.spinDC1.setRange(0, 5)
        self.spinDC1.setKeyboardTracking(False)

        self.spinDC2 = QtGui.QDoubleSpinBox()
        self.spinDC2.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinDC2.setDecimals(5)
        self.spinDC2.setSingleStep(.01)
        self.spinDC2.setRange(0, 5)
        self.spinDC2.setKeyboardTracking(False)

        self.spinDC3 = QtGui.QDoubleSpinBox()
        self.spinDC3.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinDC3.setDecimals(5)
        self.spinDC3.setSingleStep(.01)
        self.spinDC3.setRange(0, 5)
        self.spinDC3.setKeyboardTracking(False)

        self.spinDC4 = QtGui.QDoubleSpinBox()
        self.spinDC4.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinDC4.setDecimals(5)
        self.spinDC4.setSingleStep(.01)
        self.spinDC4.setRange(0, 5)
        self.spinDC4.setKeyboardTracking(False)

        # HV
        self.spinHV1 = QtGui.QDoubleSpinBox()
        self.spinHV1.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinHV1.setDecimals(0)
        self.spinHV1.setSingleStep(1)
        self.spinHV1.setRange(0, 1600)
        self.spinHV1.setKeyboardTracking(False)

        self.spinHV2 = QtGui.QDoubleSpinBox()
        self.spinHV2.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinHV2.setDecimals(0)
        self.spinHV2.setSingleStep(1)
        self.spinHV2.setRange(0, 1600)
        self.spinHV2.setKeyboardTracking(False)

        self.spinHV3 = QtGui.QDoubleSpinBox()
        self.spinHV3.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinHV3.setDecimals(0)
        self.spinHV3.setSingleStep(1)
        self.spinHV3.setRange(0, 1600)
        self.spinHV3.setKeyboardTracking(False)

        self.spinHV4 = QtGui.QDoubleSpinBox()
        self.spinHV4.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinHV4.setDecimals(0)
        self.spinHV4.setSingleStep(1)
        self.spinHV4.setRange(0, 1600)
        self.spinHV4.setKeyboardTracking(False)

        # End Cap
        self.spinEndCap1 = QtGui.QDoubleSpinBox()
        self.spinEndCap1.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinEndCap1.setDecimals(2)
        self.spinEndCap1.setSingleStep(.01)
        self.spinEndCap1.setRange(.01, 52.9)
        self.spinEndCap1.setKeyboardTracking(False)

        self.spinEndCap2 = QtGui.QDoubleSpinBox()
        self.spinEndCap2.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinEndCap2.setDecimals(2)
        self.spinEndCap2.setSingleStep(.01)
        self.spinEndCap2.setRange(0.01, 52.9)
        self.spinEndCap2.setKeyboardTracking(False)

        # Einzel lens
        self.E1Spin = QtGui.QDoubleSpinBox()
        self.E1Spin.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.E1Spin.setDecimals(0)
        self.E1Spin.setSingleStep(1)
        self.E1Spin.setRange(0, 1600)
        self.E1Spin.setKeyboardTracking(False)

        self.E2Spin = QtGui.QDoubleSpinBox()
        self.E2Spin.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.E2Spin.setDecimals(0)
        self.E2Spin.setSingleStep(1)
        self.E2Spin.setRange(0, 1600)
        self.E2Spin.setKeyboardTracking(False)


        # Use rf map switch
        self.useRFMap = QtGui.QCheckBox('Use RF Map')
        self.useRFMap.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))

        # Enable RF
        self.enableRF = QtGui.QCheckBox('Enable RF')
        self.enableRF.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))

        # Battery
        self.setCharging = QtGui.QCheckBox('Battery Charging')
        self.setCharging.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))

        #layout 1 row at a time

        layout.addWidget(freqName,             0, 1)
        layout.addWidget(phaseName,            0, 2)
        layout.addWidget(ampName,              0, 3)
        layout.addWidget(dcName,               0, 4)
        layout.addWidget(hvName,               0, 5)

        layout.addWidget(rod1Name,             1, 0)
        layout.addWidget(self.spinFreq1,       1, 1)
        layout.addWidget(self.spinPhase1,      1, 2)
        layout.addWidget(self.spinAmp1,        1, 3)
        layout.addWidget(self.spinDC1,         1, 4)
        layout.addWidget(self.spinHV1,         1, 5)

        layout.addWidget(rod2Name,             2, 0)
        layout.addWidget(self.spinFreq2,       2, 1)
        layout.addWidget(self.spinPhase2,      2, 2)
        layout.addWidget(self.spinAmp2,        2, 3)
        layout.addWidget(self.spinDC2,         2, 4)
        layout.addWidget(self.spinHV2,         2, 5)

        layout.addWidget(rod3Name,             3, 0)
        layout.addWidget(self.spinFreq3,       3, 1)
        layout.addWidget(self.spinPhase3,      3, 2)
        layout.addWidget(self.spinAmp3,        3, 3)
        layout.addWidget(self.spinDC3,         3, 4)
        layout.addWidget(self.spinHV3,         3, 5)

        layout.addWidget(rod4Name,             4, 0)
        layout.addWidget(self.spinFreq4,       4, 1)
        layout.addWidget(self.spinPhase4,      4, 2)
        layout.addWidget(self.spinAmp4,        4, 3)
        layout.addWidget(self.spinDC4,         4, 4)
        layout.addWidget(self.spinHV4,         4, 5)

        layout.addWidget(endCap1Name,          5, 0)
        layout.addWidget(self.useRFMap,        5, 3)
        layout.addWidget(self.spinEndCap1,     5, 4)

        layout.addWidget(endCap2Name,          6, 0)
        layout.addWidget(self.enableRF,        6, 3)
        layout.addWidget(self.spinEndCap2,     6, 4)

        layout.addWidget(E1Name,               7, 0)
        layout.addWidget(self.setCharging,     7, 3)
        layout.addWidget(self.E1Spin,          7, 5)

        layout.addWidget(E2Name,               8, 0)
        layout.addWidget(self.E2Spin,          8, 5)

        layout.addWidget(self.clearPhase,      9, 2, 1, 1)
        layout.addWidget(self.update_rf,       9, 3, 1, 1)
        layout.addWidget(self.update_dc,       9, 4, 1, 1)

        layout.minimumSize()

        self.setLayout(layout)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    icon = QCustomTrapGui()
    icon.show()
    app.exec_()
