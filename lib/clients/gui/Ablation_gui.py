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


class QCustomAblationGui(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setFrameStyle(0x0001 | 0x0030)
        self.makeLayout()

    def makeLayout(self):
        layout = QtGui.QGridLayout()

        shell_font = 'MS Shell Dlg 2'
        title = QtGui.QLabel('Ablation Loading')
        title.setFont(QtGui.QFont(shell_font, pointSize=16))
        title.setAlignment(QtCore.Qt.AlignCenter)

        loadingName = QtGui.QLabel('Trap Delay (usec)')
        loadingName.setFont(QtGui.QFont(shell_font, pointSize=16))
        loadingName.setAlignment(QtCore.Qt.AlignCenter)


        self.trigger_loading = QtGui.QPushButton('Ablation Load')
        self.trigger_loading.setMaximumHeight(30)
        self.trigger_loading.setMinimumHeight(30)
        self.trigger_loading.setFont(QtGui.QFont(shell_font, pointSize=14))
        self.trigger_loading.setStyleSheet("background-color: green")



        #self.update_dc.setMinimumWidth(180)

        # loading time
        self.loading_time_spin = QtGui.QDoubleSpinBox()
        self.loading_time_spin.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.loading_time_spin.setDecimals(0)
        self.loading_time_spin.setSingleStep(1)
        self.loading_time_spin.setRange(6, 200)
        self.loading_time_spin.setKeyboardTracking(False)



        #layout 1 row at a time

        layout.addWidget(title,                     0, 0, 2, 2)
        layout.addWidget(loadingName,               2, 0, 1, 2)
        layout.addWidget(self.loading_time_spin,    3, 0, 1, 2)
        layout.addWidget(self.trigger_loading,      5, 0, 1, 2)


        layout.minimumSize()

        self.setLayout(layout)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    icon = QCustomAblationGui()
    icon.show()
    app.exec_()
