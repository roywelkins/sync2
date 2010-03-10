#!/usr/bin/env python

import pywinservice
import conf

class Sync2Service(pywinservice.PyWinService):
    _svc_name_ = "sync2winservice"
    _svc_display_name_ = _svc_name_
    _svc_discription_ = "Syncer for bioverify system"
    
    def start(self):
        self.runflag = True
        while self.runflag:
            from sync2 import Sync2
            s = Sync2()
            s.syncall()
            self.sleep(conf.sync_internal)
    
    def stop(self):
        self.runflag = False
        
if __name__=='__main__':
    #pywinservice.installAndStartService(Sync2Service)
    import win32serviceutil
    win32serviceutil.HandleCommandLine(Sync2Service)