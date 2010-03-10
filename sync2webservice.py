#!/usr/bin/env python
# coding:utf8

from soaplib.wsgi_soap import SimpleWSGISoapApp
from soaplib.service import soapmethod
from soaplib.serializers.primitive import String, Integer, Array
from soaplib.serializers.binary import Attachment

import os
import time
import serverconf
import baseconf
import logger
import xmlmgr
import db
import exceptions
from xml.etree import cElementTree as ElementTree

class Sync2WebService(SimpleWSGISoapApp):
    
    log = logger.Logger('logs', 'sync2service.log.'+time.strftime('%Y%m%d', time.localtime())+'.txt')
    
    def getNewDb(self):
        d = db.Db(serverconf.mysql_options)        
        d.log = Sync2WebService.log
        return d
    
    def __init__(self):
        SimpleWSGISoapApp.__init__(self)
        self.xmlmgr = xmlmgr.XMLManager()
        self.log = Sync2WebService.log

    @soapmethod(String)
    def test_connection(self, msg):
        self.log.write(msg)

    @soapmethod(_returns=String)
    def getCurrentTime(self):
        #TODO: 应该在这测试一下是否能连接mysql，不能的话试图重连
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    @soapmethod(String, String, String, _returns=String)
    def getKeysToSync(self, table, lasttime, nexttime):
        try:
            if lasttime>=nexttime:
                return ''
            re = self.getNewDb().getKeysInTableWithSyncBetween(table, lasttime, nexttime)
            if not re:
                return ''
            else:
                return ','.join(re)
        except Exception, e:
            self.log.write(e)
            raise

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
            f = open(fullpath, 'wb')
            f.write(data.data)
            f.close()
        except Exception, e:
            self.log.write(e)
            raise

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
        except exceptions.IOError, e:
            if e.errno==2:
                self.log.write('error: no such file: %s' % (filepath, ))
                return Attachment(data='None')
            else:
                raise
        
    @soapmethod(String, _returns=String)    
    def upload(self, xmlstring):
        """accept data from client and update it to the database
        
        currently, we don't check if data is duplicated, i.e., if it is duplicated,
        the old one is deleted.
        """
        d = self.xmlmgr.XMLToDict(xmlstring)
        table = d['table']
        data = d['data']
        data['sync'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.getNewDb().updateData(table, data)
        return data['sync']

    @soapmethod(String, String, _returns=String)    
    def download(self, table, key):
        try:
            datas = self.getNewDb().getDatas(table, '%s = "%s" limit 1' % (baseconf.keys[table], key))
            if not datas:
                return None
            data = datas[0]
            datadict = {}
            datadict['table']=table
            datadict['method'] = 'download'
            datadict['data'] = data
            xe = self.xmlmgr.dictToXML(datadict,'root')
            xs = ElementTree.tostring(xe, encoding='utf8')
            return xs
        except Exception, e:
            self.log.write(e)
            raise
        
    @soapmethod()
    def fixAll(self):
        #card_info
        d = self.getNewDb()
        d.executeSQL('update card_info set person_id = (select person_id from person_info where person_info.student_id = card_info.student_id) where person_id is null')
        db.executeSQL('update card_info set person_uuid = (select uuid from person_info where person_info.student_id = card_info.student_id) where person_uuid is null')
        #class
        db.executeSQL('update class set person_id = (select person_id from person_info where person_info.uuid = class.person_uuid) where person_id is null')
        #sample
        db.executeSQL('update sample set person_id = (select person_id from person_info where person_info.uuid = sample.person_uuid) where person_id is null')
        db.executeSQL('update sample set class_id = (select class_id from class where class.uuid = sample.class_uuid) where class_id is null')
        #template
        db.executeSQL('update template set person_id = (select person_id from person_info where person_info.uuid = template.person_uuid) where person_id is null')
        db.executeSQL('update template set class_id = (select class_id from class where class.uuid = template.class_uuid) where class_id is null')
        db.executeSQL('update template set sample_id = (select sample_id from sample where sample.uuid = template.sample_uuid) where sample_id is null')
        
        db.recordDeduplicate()
        db.genResult()
        


if __name__=='__main__':
#    s = Sync2WebService()
#    s.putFile('/tmp/1/2', None)
#    exit()
    #s = Sync2WebService()
    #s.fixAll()
    #exit()
    try:
        #from wsgiref.simple_server import make_server
        #server = make_server('0.0.0.0',7789,Sync2WebService())
        #server.serve_forever()
        
        from cherrypy.wsgiserver import CherryPyWSGIServer
        server = CherryPyWSGIServer(('0.0.0.0',7789),Sync2WebService())
        server.start()
    except KeyboardInterrupt, e:
        print e