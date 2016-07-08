from datetime import datetime
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from labrad.gpib import GPIBManagedServer, GPIBDeviceWrapper

#def hyper_task(a):
#    print "I like to run fast", datetime.now(),a

def tired_task():
    print "I want to run slowly", datetime.now()

class xclass(GPIBManagedServer):

    
    lc = LoopingCall(lambda a='a':hyper_task(a))
    lc.start(0.1)

    def hyper_task(self, a):
        print "I like to run fast", datetime.now(),a

if __name__ == "__main__":
    from labrad import util
    x = xclass()
    util.runServer(x)

#reactor.run()
