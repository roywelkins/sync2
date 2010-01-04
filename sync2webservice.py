#!/usr/bin/env python

from soaplib.wsgi_soap import SimpleWSGISoapApp
from soaplib.service import soapmethod
from soaplib.serializers.primitive import String, Integer, Array
from soaplib.serializers.binary import Attachment

import os
import time
import serverconf

class Sync2WebService(SimpleWSGISoapApp):

    @soapmethod(String)
    def test_connection(self, msg):
        print msg

    @soapmethod(_returns=String)
    def getCurrentTime(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    @soapmethod(String, Attachment, _returns=String)
    def putFile(self, filepath, data):
        if os.sep=='/':
            filepath = filepath.replace('\\', '/')
        else:
            filepath = filepath.replace('/', '\\')
        fullpath = os.path.join(serverconf.data_dir_root, filepath)
        if not os.path.isdir(os.path.dirname(fullpath)):
            os.makedirs(os.path.dirname(fullpath))
        f = open(fullpath, 'w')
        f.write(data.data)
        f.close()

    @soapmethod(String, _returns=Attachment)
    def getFile(self, filepath):
        if os.sep=='/':
            filepath = filepath.replace('\\', '/')
        else:
            filepath = filepath.replace('/', '\\')
        fullpath = os.path.join(serverconf.data_dir_root, filepath)
        f = open(fullpath, 'rb')
        data = f.read()
        f.close()
        return Attachment(data=data)


if __name__=='__main__':
#    s = Sync2WebService()
#    s.putFile('/tmp/1/2', None)
#    exit()
    try:
        from wsgiref.simple_server import make_server
        server = make_server('0.0.0.0',7789,Sync2WebService())
        server.serve_forever()
    except KeyboardInterrupt, e:
        print e
