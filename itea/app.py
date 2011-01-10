# Copyright (c) 2011 Arjan Scherpenisse
# See LICENSE for details.

"""
itea?
"""
import os

from sparked import application
from sparked.hardware import rfid

from itea.gfx import Stage


class Application(application.Application):

    def started(self):
        self.lines = [os.popen("fortune -s -o").readlines()[0].strip() for x in xrange(100)]
        self.stage = Stage(self)

        mon = rfid.RFIDMonitor()
        mon.addCandidate(rfid.SonMicroProtocol, 19200)
        mon.setServiceParent(self)

        rfid.rfidEvents.addObserver("tag-added", lambda tag: self.stage.addLine("Tag: " + tag['tag']))
