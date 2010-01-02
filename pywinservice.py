#!/usr/bin/env python

import os
from os.path import splitext, abspath
from sys import modules

import win32service
import win32serviceutil
import win32event
import win32api
import servicemanager

class PyWinService(win32serviceutil.ServiceFramework):
    """Overide this to implement your own service"""
    
    # to be override
    _svc_name_ = None
    _svc_display_name_ = None
    _svc_description_ = None
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.log('init')
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        
    def log(self, msg):
        """log msg into windows log"""
        servicemanager.LogInfoMsg(str(msg))
    
    def sleep(self, sec):
        """sleep sec seconds"""
        win32api.Sleep(sec*1000, True)
        pass
       
    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        try:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.log('start')
            self.start()
            self.log('wait')
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            self.log('done')
        except Exception, x:
            self.log('Exception: %s' % x)
            self.SvcStop()
       
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.log('stopping')
        self.stop()
        self.log('stopped')
        win32event.SetEvent(self.hWaitStop)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        
    # to be override
    def start(self):
        pass
    
    def stop(self):
        pass
    
def installAndStartService(cls):
    """As the function name says"""
    
    win32api.SetConsoleCtrlHandler(lambda x: True, True)
    try:
        module_path = modules[cls.__module__].__file__
    except AttributeError:
        from sys import executable
        module_path = executable
    module_file = splitext(abspath(module_path))[0]
    cls._svc_reg_class_ = '%s.%s' % (module_file, cls.__name__)
    # stop and delete service if already exists
    try:
        win32serviceutil.StopService(cls._svc_name_)
    except Exception, e:
        print e
    try:
        win32serviceutil.RemoveService(cls._svc_name_)
    except Exception, e:
        print e
    # install the service
    try:
        win32serviceutil.InstallService(
            cls._svc_reg_class_,
            cls._svc_name_,
            cls._svc_display_name_,
            startType = win32service.SERVICE_AUTO_START
        )
        print "service installed"
        win32serviceutil.StartService(cls._svc_name_)
        print "service started"
    except Exception, e:
        print ('failed: Exception: %s ' % e)
        
