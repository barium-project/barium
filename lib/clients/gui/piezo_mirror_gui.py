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


class QPiezoMirrorGui(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setFrameStyle(0x0001 | 0x0030)
        self.makeLayout()

    def makeLayout(self):
        layout = QtGui.QGridLayout()

        shell_font = 'MS Shell Dlg 2'
        VoltageName = QtGui.QLabel('Voltage(V)')
        VoltageName.setFont(QtGui.QFont(shell_font, pointSize=16))
        VoltageName.setAlignment(QtCore.Qt.AlignCenter)

       
       
        Ch = QtGui.QLabel('Mirror 1')
        Ch.setFont(QtGui.QFont(shell_font, pointSize=16))
        Ch.setAlignment(QtCore.Qt.AlignCenter)
        Ch2 = QtGui.QLabel('Mirror 2')
        Ch2.setFont(QtGui.QFont(shell_font, pointSize=16))
        Ch2.setAlignment(QtCore.Qt.AlignCenter)

        
        xaxis1 = QtGui.QLabel('X Axis')
        xaxis1.setFont(QtGui.QFont(shell_font, pointSize=16))
        xaxis1.setAlignment(QtCore.Qt.AlignCenter)
        yaxis1 = QtGui.QLabel('Y Axis')
        yaxis1.setFont(QtGui.QFont(shell_font, pointSize=16))
        yaxis1.setAlignment(QtCore.Qt.AlignCenter)

         
        xaxis2 = QtGui.QLabel('X Axis')
        xaxis2.setFont(QtGui.QFont(shell_font, pointSize=16))
        xaxis2.setAlignment(QtCore.Qt.AlignCenter)
        yaxis2 = QtGui.QLabel('Y Axis')
        yaxis2.setFont(QtGui.QFont(shell_font, pointSize=16))
        yaxis2.setAlignment(QtCore.Qt.AlignCenter)
                # frequency
        self.SpinVoltage = QtGui.QDoubleSpinBox()
        self.SpinVoltage.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.SpinVoltage.setDecimals(3)
        self.SpinVoltage.setSingleStep(.001)
        self.SpinVoltage.setRange(0, 150)
        self.SpinVoltage.setValue(125)
        self.SpinVoltage.setKeyboardTracking(False)

        self.SpinVoltage2 = QtGui.QDoubleSpinBox()
        self.SpinVoltage2.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.SpinVoltage2.setDecimals(3)
        self.SpinVoltage2.setSingleStep(.001)
        self.SpinVoltage2.setRange(0, 150)
        self.SpinVoltage2.setValue(125)

        self.SpinVoltage3 = QtGui.QDoubleSpinBox()
        self.SpinVoltage3.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.SpinVoltage3.setDecimals(3)
        self.SpinVoltage3.setSingleStep(.001)
        self.SpinVoltage3.setRange(0, 150)
        self.SpinVoltage3.setValue(125)

        self.SpinVoltage4 = QtGui.QDoubleSpinBox()
        self.SpinVoltage4.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.SpinVoltage4.setDecimals(3)
        self.SpinVoltage4.setSingleStep(.001)
        self.SpinVoltage4.setRange(0, 150)
        self.SpinVoltage4.setValue(125)

        self.SpinVoltage2.setKeyboardTracking(False)
        self.SpinVoltage3.setKeyboardTracking(False)

        self.SpinVoltage4.setKeyboardTracking(False)

        
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
        self.volt_switch = QtGui.QPushButton('Voltage on/off')
        self.volt_switch.setMinimumHeight(30)
        self.volt_switch.setMinimumWidth(100)
        self.volt_switch.setMaximumWidth(100)
        self.volt_switch.setCheckable(True)

        self.volt_switch2 = QtGui.QPushButton('Voltage on/off')
        self.volt_switch2.setMinimumHeight(30)
        self.volt_switch2.setMinimumWidth(100)
        self.volt_switch2.setMaximumWidth(100)
        self.volt_switch2.setCheckable(True)


        self.volt_switch3 = QtGui.QPushButton('Voltage on/off')
        self.volt_switch3.setMinimumHeight(30)
        self.volt_switch3.setMinimumWidth(100)
        self.volt_switch3.setMaximumWidth(100)
        self.volt_switch3.setCheckable(True)

        self.volt_switch4 = QtGui.QPushButton('Voltage on/off')
        self.volt_switch4.setMinimumHeight(30)
        self.volt_switch4.setMinimumWidth(100)
        self.volt_switch4.setMaximumWidth(100)
        self.volt_switch4.setCheckable(True)
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
        layout.addWidget(Ch2,             3, 1)

        layout.addWidget(VoltageName,             0, 2)
        #layout.addWidget(ampName,              0, 3)
        layout.addWidget(self.SpinVoltage,             1, 2)
        #layout.addWidget(self.spinAmp,              1, 3)
        layout.addWidget(self.SpinVoltage2,             2, 2)
        #layout.addWidget(self.spinAmp2,              2, 3)
        layout.addWidget(self.SpinVoltage3,             4, 2)
        layout.addWidget(self.SpinVoltage4,             5, 2)

        
        layout.addWidget(self.volt_switch, 1,4)
        layout.addWidget(self.volt_switch2, 2,4)

        layout.addWidget(self.volt_switch3, 4,4)
        layout.addWidget(self.volt_switch4, 5,4)

        layout.addWidget(xaxis1,              1, 1)
        layout.addWidget(yaxis1,              2, 1)
        layout.addWidget(xaxis2,              4, 1)
        layout.addWidget(yaxis2,              5, 1)


        #layout.minimumSize()

        self.setLayout(layout)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    icon = QPiezoMirrorGui()
    icon.show()
    app.exec_()
