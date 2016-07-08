#This is an example on how to implement for loops in an asynchronous program
#This includes a timed for loop, nested in a for loop, nested in a for loop
#It is messy but it gets the job done.
#This is similar to the synchronous for loop algorithm:
#toploop(k to kmax)
#   <toploop stuff>
#   nestloop(j to jmax)
#       <nestloop stuff>
#       forloop(i to imax)
#           <forloop stuff>
#Follow the numbers for a tour of the code.
#- Calvin He

from PyQt4 import QtCore, QtGui
from twisted.internet.defer import inlineCallbacks

class Async_Loop_Example(object):
    def __init__(self, reactor, parent = None):
        super(Async_Loop_Example, self).__init__()
        self.reactor = reactor
        self.initialize()
    @inlineCallbacks
    def initialize(self):
        print 'program starting'
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda :self.timer_tick()) #5) The timeout signal had been initially connected to the .timer_tick() slot
        self.toploop(0,2)   #1) Calls the toploop(iterates from 0 to 1)
        yield None
    @inlineCallbacks
    def forloop(self, i, imax, tick_time):
        self.i = i
        self.imax = imax
        self.tick_time = tick_time
        self.timer.start(tick_time) #4) forloop starts the timer, which generates a .timeout() signal every tick_time
        yield None
    @inlineCallbacks
    def timer_tick(self):
        if self.i<self.imax:
            print self.i
            self.i += 1
        else:
            self.timer.stop()
            self.i = 0
            self.nestloop(self.j, self.jmax) #6) forloop iterates until it is done, and then calls its nestloop for the next iteration (all iteration parameters is saved to the object)
        yield None
    @inlineCallbacks
    def nestloop(self, j, jmax):
        self.j = j
        self.jmax = jmax
        if self.j<self.jmax:
            print str(self.j)+'....'
            self.forloop(0,5,1000)#3) nestloop performs stuff and then initiates the timed forloop(iterates from 0 to 5 with 1000ms per loop)
            self.j += 1
        else:
            self.toploop(self.k, self.kmax) #7) nestloop iterates, calling new forloops each iteration, until it is done, and then calls toploop for the next iteration
        yield None
    @inlineCallbacks
    def toploop(self, k, kmax):
        self.k = k
        self.kmax = kmax
        if self.k<self.kmax:
            print str(self.k)+'----'
            self.nestloop(0,3)  #2) toploop performs stuff, and then initiates the nestloop(iterates from 0 to 2)
            self.k += 1
        else:
            print 'program stopped' #8) When toploop finishes its lass iteration, it performs this command
        yield None
        
        
        

if __name__ == "__main__":
    a = QtGui.QApplication ([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    client = Async_Loop_Example(reactor)

    reactor.run()
    
    sys.exit(a.exec_())
