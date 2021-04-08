import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QSlider,
                             QVBoxLayout, QApplication)

from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet.defer import Deferred, inlineCallbacks

the_client = None


class Echo(Protocol):
    total = 0
    def __init__(self):

        print("Echo id: ")
        global the_client
        the_client = self
        self.numProtocols = 0
        Echo.total += 1
        self.id = Echo.total

        
    def connectionMade(self):
        print("Client: connection made: ", self.id)
        self.factory.d1.callback("success")

    def connectionLost(self, reason):
        global the_client
        the_client = None
        print(reason)

    def dataReceived(self, data):
        print("Client Got Data ", data)

    def __del__(self):
        print("Gone")


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        lcd = QLCDNumber(self)
        sld = QSlider(Qt.Horizontal, self)

        vbox = QVBoxLayout()
        vbox.addWidget(lcd)
        vbox.addWidget(sld)

        self.setLayout(vbox)
        sld.valueChanged.connect(lcd.display)
        sld.valueChanged.connect(self.updateValue)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Signal and slot')
        self.show()

    def updateValue(self, value):
        if the_client is not None:
            byte_str = str.encode(str(value))
            the_client.transport.write(byte_str)

factory = ClientFactory()
factory.protocol = Echo

@inlineCallbacks
def wait_for_it():
    print('before await')
    the_result = yield factory.d1
    print(f'result = {the_result}')
    return the_result


@inlineCallbacks
def meth():
    print("called")
    factory.d1 = Deferred()
    reactor.connectTCP('localhost', 8007, factory)
    yield wait_for_it()


app = QApplication(sys.argv) 
import qt5reactor
qt5reactor.install()


example = Example()
example.show()
from twisted.internet import reactor
reactor.callLater(1.0, meth)

reactor.run()

