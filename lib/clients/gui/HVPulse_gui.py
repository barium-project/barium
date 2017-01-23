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


class QCustomHVPulseGui(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setFrameStyle(0x0001 | 0x0030)
        self.makeLayout()

    def makeLayout(self):
        layout = QtGui.QGridLayout()

        shell_font = 'MS Shell Dlg 2'
        title = QtGui.QLabel('TOF')
        title.setFont(QtGui.QFont(shell_font, pointSize=16))
        title.setAlignment(QtCore.Qt.AlignCenter)

        self.hv_pulse = QtGui.QPushButton('HV Pulse')
        self.hv_pulse.setMaximumHeight(30)
        self.hv_pulse.setMinimumHeight(30)
        self.hv_pulse.setFont(QtGui.QFont(shell_font, pointSize=14))
        self.hv_pulse.setStyleSheet("background-color: green")

        self.hv_graph = QtGui.QPushButton(' HV Pulse/Graph')
        self.hv_graph.setMaximumHeight(30)
        self.hv_graph.setMinimumHeight(30)
        self.hv_graph.setFont(QtGui.QFont(shell_font, pointSize=14))
        self.hv_graph.setStyleSheet("background-color: green")


        #layout 1 row at a time

        layout.addWidget(title,                     0, 0, 1, 2)
        layout.addWidget(self.hv_pulse,             3, 0, 1, 2)
        layout.addWidget(self.hv_graph,             4, 0, 1, 2)



        layout.minimumSize()

        self.setLayout(layout)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    icon = QCustomHVPulseGui()
    icon.show()
    app.exec_()
