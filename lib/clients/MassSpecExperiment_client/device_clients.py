from barium.lib.clients.HP6033A_client.HP6033Aclient import HP6033A_Client
from barium.lib.clients.RGA_client.RGAclient import RGA_Client
from barium.lib.clients.Scalar_client.Scalarclient import SR430_Scalar_Client

from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui, QtCore
import time
import numpy as np
import ctypes
from datetime import datetime

if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    from socket import gethostname

    hpclient = HP6033A_Client(reactor)
    hpclient.self_connect('127.0.0.1',gethostname())
    hpclient.show()

    scaclient = SR430_Scalar_Client(reactor)
    scaclient.self_connect('127.0.0.1',gethostname())
    scaclient.show()

    rgaclient = RGA_Client(reactor)
    rgaclient.self_connect('127.0.0.1',gethostname())
    rgaclient.show()

    reactor.run()
