#!/usr/bin/env python
"""The code that do the real things about syncing."""

from suds.client import Client
import conf

class Sync2:
    def syncall(self):
        print conf.sync_internal
        pass

#url = 'http://162.105.81.81/BV_Upload/BVServicePort?wsdl'
#service = Client(url).service
#service.test_connection("lala")

if __name__=='__main__':
    s = Sync2()
    s.syncall()