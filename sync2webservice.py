#!/usr/bin/env python

from soaplib.wsgi_soap import SimpleWSGISoapApp
from soaplib.service import soapmethod
from soaplib.serializers.primitive import String, Integer, Array
from soaplib.serializers.binary import Attachment

import os
import time
import serverconf
import conf
import logger
import xmlmgr
import db

class Sync2WebService(SimpleWSGISoapApp):
    
    def init(self):
        self.xmlmgr = xmlmgr.XMLManager()
        self.db = db.Db(serverconf.mysql_options)
        self.log = logger.Logger('logs', 'sync2service.log.'+time.strftime('%Y%m%d', time.localtime())+'.txt')
        self.db.log = self.log

    @soapmethod(String)
    def test_connection(self, msg):
        print msg

    @soapmethod(_returns=String)
    def getCurrentTime(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    @soapmethod(String, Attachment)
    def putFile(self, filepath, data):
        try:
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
        except Exception, e:
            self.log.write(e)

    @soapmethod(String, _returns=Attachment)
    def getFile(self, filepath):
        try:
            if os.sep=='/':
                filepath = filepath.replace('\\', '/')
            else:
                filepath = filepath.replace('/', '\\')
            fullpath = os.path.join(serverconf.data_dir_root, filepath)
            f = open(fullpath, 'rb')
            data = f.read()
            f.close()
            return Attachment(data=data)
        except Exception, e:
            self.log.write(e)
            return None
        
    @soapmethod(String, _returns=String)    
    def upload(self, xmlstring):
        """accept data from client and update it to the database
        
        currently, we don't check if data is duplicated, i.e., if it is duplicated,
        the old one is deleted.
        """
        d = self.xmlmgr.XMLToDict(xmlstring)
        table = d['table']
        data = table['data']
        data['sync'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.db.updateData(table, data)
        return data['sync']
        
    @soapmethod(String, String, _returns=String)    
    def download(self, table, key):
        try:
            datas = d.getDatas(table, '%s = "%s" limit 1' % (conf.keys[table], key))
            if not datas:
                return None
            data = datas[0]
            datadict = {}
            datadict['table']=table
            datadict['method'] = 'download'
            datadict['data'] = data
            xe = x.dictToXML(datadict,'root')
            xs = ElementTree.tostring(xe, encoding='utf8')
            return xs
        except Exception, e:
            self.log.write(e)
        


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