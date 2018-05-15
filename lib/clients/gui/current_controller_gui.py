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


class QCustomCurrentGui(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setFrameStyle(0x0001 | 0x0030)
        self.makeLayout()

    def makeLayout(self):
        layout = QtGui.QGridLayout()

        shell_font = 'MS Shell Dlg 2'
        title = QtGui.QLabel('Current Controller')
        title.setFont(QtGui.QFont(shell_font, pointSize=16))
        title.setAlignment(QtCore.Qt.AlignCenter)

        loadingName = QtGui.QLabel('Current (mA)')
        loadingName.setFont(QtGui.QFont(shell_font, pointSize=16))
        loadingName.setAlignment(QtCore.Qt.AlignCenter)


        self.output = TextChangingButton(('On','Off'))
        self.output.setMaximumHeight(30)
        self.output.setMinimumHeight(30)
        self.output.setFont(QtGui.QFont(shell_font, pointSize=14))

        #self.update_dc.setMinimumWidth(180)

        # loading time
        self.current_spin = QtGui.QDoubleSpinBox()
        self.current_spin.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.current_spin.setDecimals(3)
        self.current_spin.setSingleStep(.05)
        self.current_spin.setRange(0, 700)
        self.current_spin.setKeyboardTracking(False)



        #layout 1 row at a time

        layout.addWidget(title,                     0, 0, 2, 2)
        layout.addWidget(loadingName,               2, 0, 1, 2)
        layout.addWidget(self.current_spin,    3, 0, 1, 2)
        layout.addWidget(self.output,      5, 0, 1, 2)


        layout.minimumSize()

        self.setLayout(layout)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    icon = QCustomCurrentGui()
    icon.show()
    app.exec_()
