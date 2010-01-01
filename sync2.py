#!/usr/bin/env python
"""The code that do the real things about syncing."""

import suds
import conf

class Sync2:
    _service = suds.client.Client(conf.web_service_url).service
        
    def syncall(self):
        self._service.test_connection("lalala")
    
    

if __name__=='__main__':
    s = Sync2()
    s.syncall()