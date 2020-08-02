from barium.lib.clients.gui.Bristol_gui import QCustomBristol
from barium.lib.clients.gui.q_custom_text_changing_button import \
    TextChangingButton
from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui
try:
    from config.bristol_config import bristol_config
except:
    from barium.lib.config.bristol_config import bristol_config

import socket
import os

SIGNALID1 = 445566
SIGNALID2 = 444333


class bristol_client(QtGui.QWidget):

    def __init__(self, reactor, parent=None):
        """initializels the GUI creates the reactor
            and empty dictionary for channel widgets to
            be stored for iteration. also grabs chan info
            from multiplexer_config
        """
        super(bristol_client, self).__init__()
        self.password = os.environ['LABRADPASSWORD']
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.name = socket.gethostname() + ' Bristol Client'
        self.d = {}
        self.connect()
        self._check_window_size()

    def _check_window_size(self):
        """Checks screen size to make sure window fits in the screen. """
        desktop = QtGui.QDesktopWidget()
        screensize = desktop.availableGeometry()
        width = screensize.width()
        height = screensize.height()
        min_pixel_size = 1080
        if (width <= min_pixel_size or height <= min_pixel_size):
            self.showMaximized()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to the Bristol computer and
        connects incoming signals to relavent functions

        """
        self.wavemeterIP = bristol_config.ip
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(self.wavemeterIP,
                                      name=self.name,
                                      password=self.password)
        self.server = yield self.cxn.bristolserver
        yield self.server.signal__frequency_changed(SIGNALID1)
        yield self.server.signal__amplitude_changed(SIGNALID2)

        yield self.server.addListener(listener = self.updateFrequency, source = None, ID = SIGNALID1)
        yield self.server.addListener(listener = self.updateAmplitude, source = None, ID = SIGNALID2)

        self.initializeGUI()

        
    @inlineCallbacks
    def initializeGUI(self):

        initstartvalue = yield self.server.get_frequency()
        layout = QtGui.QGridLayout()
        self.setWindowTitle('Bristol Wavemeter')
        qBox = QtGui.QGroupBox('Wave Length')
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0)
        widget = QCustomBristol('Under Exposed',False)
        self.d[0] = widget
        subLayout.addWidget(self.d[0],1,0)
        self.setLayout(layout)
    
    
    def updateFrequency(self , c , signal):
        freq = signal
        self.d[0].currentfrequency.setText(str(freq))
        
    
    def updateAmplitude(self , c , signal):
        amp = signal
        self.d[0].powermeter.setValue(amp)

    def closeEvent(self, x):
        self.reactor.stop()
   



if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    wavemeterWidget = bristol_client(reactor)
    wavemeterWidget.show()
    reactor.run()
