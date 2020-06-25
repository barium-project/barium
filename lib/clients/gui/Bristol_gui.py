import sys
from PyQt4 import QtGui, QtCore
from barium.lib.clients.gui.QCustomPowerMeter import MQProgressBar
from barium.lib.clients.gui.QCustomSlideIndicator import SlideIndicator
from barium.lib.clients.gui.q_custom_text_changing_button import \
    TextChangingButton as _TextChangingButton


class StretchedLabel(QtGui.QLabel):
    def __init__(self, *args, **kwargs):
        QtGui.QLabel.__init__(self, *args, **kwargs)
        self.setMinimumSize(QtCore.QSize(350, 100))

    def resizeEvent(self, evt):

        font = self.font()
        font.setPixelSize(self.width() * 0.14 - 14)
        self.setFont(font)


class TextChangingButton(_TextChangingButton):
    def __init__(self, button_text=None, parent=None):
        super(TextChangingButton, self).__init__(button_text, parent)
        self.setMaximumHeight(30)


class QCustomBristol(QtGui.QFrame):
    def __init__(self, frequency, stretchedlabel, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setFrameStyle(0x0001 | 0x0030)
        self.makeLayout(frequency, stretchedlabel)

    def makeLayout(self, frequency, stretchedlabel):
        layout = QtGui.QGridLayout()

        shell_font = 'MS Shell Dlg 2'
   

       

        

        self.powermeter = MQProgressBar()
        self.powermeter.setOrientation(QtCore.Qt.Vertical)
        self.powermeter.setMeterColor("orange", "red")
        self.powermeter.setMeterBorder("orange")

        
        if stretchedlabel is True:
            self.currentfrequency = StretchedLabel(frequency)
        else:
            self.currentfrequency = QtGui.QLabel(frequency)


        self.currentfrequency.setFont(QtGui.QFont(shell_font, pointSize=60))
        self.currentfrequency.setAlignment(QtCore.Qt.AlignCenter)
        self.currentfrequency.setMinimumWidth(600)

    
        layout.addWidget(self.currentfrequency, 1, 0, 4, 2)

        layout.addWidget(self.powermeter,       0,3,7,1)

        layout.minimumSize()

        self.setLayout(layout)

    def setExpRange(self, exprange):
        self.spinExp.setRange(exprange)

    def setFreqRange(self, freqrange):
        self.spinFreq.setRange(freqrange)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    icon = QCustomBristol('Under Exposed',False)
    icon.show()
    app.exec_()
