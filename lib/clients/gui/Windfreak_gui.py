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


class QWindfreakGui(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setFrameStyle(0x0001 | 0x0030)
        self.makeLayout()

    def makeLayout(self):
        layout = QtGui.QGridLayout()

        shell_font = 'MS Shell Dlg 2'
        freqName = QtGui.QLabel('Frequency (MHz)')
        freqName.setFont(QtGui.QFont(shell_font, pointSize=16))
        freqName.setAlignment(QtCore.Qt.AlignCenter)

       
        ampName = QtGui.QLabel('RF Amp (dB)')
        ampName.setFont(QtGui.QFont(shell_font, pointSize=16))
        ampName.setAlignment(QtCore.Qt.AlignCenter)
        Ch = QtGui.QLabel('Channel')
        Ch.setFont(QtGui.QFont(shell_font, pointSize=16))
        Ch.setAlignment(QtCore.Qt.AlignCenter)
                # frequency
        self.spinFreq = QtGui.QDoubleSpinBox()
        self.spinFreq.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinFreq.setDecimals(6)
        self.spinFreq.setSingleStep(1)
        self.spinFreq.setRange(53, 1400)
        self.spinFreq.setValue(125)

        self.spinFreq.setKeyboardTracking(False)

        self.spinFreq_ = QtGui.QDoubleSpinBox()
        self.spinFreq_.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinFreq_.setDecimals(6)
        self.spinFreq_.setSingleStep(1)
        self.spinFreq_.setRange(53, 1400)
        self.spinFreq_.setValue(125)

        self.spinFreq_.setKeyboardTracking(False)
        
        # Amplitude
        self.spinAmp = QtGui.QDoubleSpinBox()
        self.spinAmp.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinAmp.setDecimals(0)
        self.spinAmp.setSingleStep(1)
        self.spinAmp.setRange(-60, 20)
        self.spinAmp.setValue(-60)
        self.spinAmp.setKeyboardTracking(False)

        self.spinAmp2 = QtGui.QDoubleSpinBox()
        self.spinAmp2.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinAmp2.setDecimals(0)
        self.spinAmp2.setSingleStep(1)
        self.spinAmp2.setRange(-60, 20)
        self.spinAmp2.setValue(-60)
        self.spinAmp2.setKeyboardTracking(False)

        #make on off switch
        self.rf_switch = QtGui.QPushButton('RF on/off')
        self.rf_switch.setMinimumHeight(30)
        self.rf_switch.setMinimumWidth(100)
        self.rf_switch.setMaximumWidth(100)
        self.rf_switch.setCheckable(True)

        self.rf_switch2 = QtGui.QPushButton('RF on/off')
        self.rf_switch2.setMinimumHeight(30)
        self.rf_switch2.setMinimumWidth(100)
        self.rf_switch2.setMaximumWidth(100)
        self.rf_switch2.setCheckable(True)
        #self.amptext=QtGui.QLineEdit()
        #self.amptext.setFont(QtGui.QFont(shell_font, pointSize=16))
        #self.amptext.setReadOnly(True)


        # Channel A switch
        self.usechA = QtGui.QPushButton("Use Channel A")
        self.usechA.setCheckable(False)
        self.usechA.setMinimumHeight(30)
        self.usechA.setMinimumWidth(100)
        self.usechA.setMaximumWidth(100)
        #self.usechA.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))

        # Channel B Switch
        self.usechB = QtGui.QPushButton("Use Channel B")
        self.usechB.setCheckable(False)
        self.usechB.setMinimumHeight(30)
        self.usechB.setMinimumWidth(100)
        self.usechB.setMaximumWidth(100)
        #self.usechB.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))
        # Battery
        self.setCharging = QtGui.QCheckBox('Battery Charging')
        self.setCharging.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))

        #layout 1 row at a time
        layout.addWidget(Ch,             0, 1)
        layout.addWidget(freqName,             0, 2)
        layout.addWidget(ampName,              0, 3)
        layout.addWidget(self.spinFreq,             1, 2)
        layout.addWidget(self.spinAmp,              1, 3)
        layout.addWidget(self.spinFreq_,             2, 2)
        layout.addWidget(self.spinAmp2,              2, 3)

        
        layout.addWidget(self.rf_switch, 1,4)
        layout.addWidget(self.rf_switch2, 2,4)


        layout.addWidget(self.usechA,              1, 1)
        layout.addWidget(self.usechB,              2, 1)


        #layout.minimumSize()

        self.setLayout(layout)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    icon = QWindfreakGui()
    icon.show()
    app.exec_()
