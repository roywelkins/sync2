#!/usr/bin/env python
"""The code that controls the syncer workflow"""

import os
import traceback
import time
import soaplib.client
from soaplib.serializers.binary import Attachment
from xml.etree import ElementTree
import socket
#from xml.etree.ElementTree import Element

import conf
import plugin
import db
import xmlmgr
from sync2webservice import Sync2WebService
import logger
import exceptions
import util
from util.getip import get_ip_address
import os

class Sync2: 
    def __init__(self):
        self.log = logger.Logger(conf.logdir, 'sync2.log.'+time.strftime('%Y%m%d', time.localtime())+'.txt')
        self.xmlmgr = xmlmgr.XMLManager()
        try:
            self.service = soaplib.client.make_service_client(conf.web_service_url, Sync2WebService())
            #self.service = Sync2WebService()
            self.log.write('checking connection with url: ' + conf.web_service_url)
            self.service.test_connection(os.getenv('computername') + ' ' + get_ip_address())
            self.next_sync_time = self.service.getCurrentTime()
            self.log.write('server connected: ' + self.next_sync_time)
        except socket.error, e:
            self.log.write('fatal error: could not connect to server %s ' % conf.web_service_url)
            raise
                
        try:
            self.db = db.Db(conf.mysql_options)
            self.db.log = self.log
            self.last_sync_time = self.db.getLastSyncTime()
        except Exception, e:
            self.log.write(e)
            raise
        
    def syncAll(self):
        self.service.fixAll()
        return
        
        if conf.is_register_server:
            upload_tables = conf.server_upload_tables + conf.common_upload_tables
        else:
            upload_tables = conf.common_upload_tables
        for table in upload_tables:
            self.uploadTable(table)
            
        if conf.is_register_server:
            download_tables = conf.server_download_tables + conf.common_download_tables
        else:
            download_tables = conf.common_download_tables
        for table in download_tables:
            self.downloadTable(table)
        
        self.service.fixAll()
        self.db.setLastSyncTime(self.next_sync_time)
    
    def uploadTable(self, table):
        try:
            self.log.write('upload: %s' % (table,))
            plug = self.getPlugin(table)
            plug.preUpload()
            datas = self.db.getDatas(table, 'sync=0 and "%s" is not null' % conf.keys[table])
            if not datas:
                return
            total = len(datas)
            i = 1
            for data in datas:
                try:
                    print '\r', i,'/',total,
                    i = i+1
                    data = plug.preUploadData(data)
                    self.uploadData(table,data)
                    data = plug.postUploadData(data)
                except Exception, e:
                    self.log.write(e)
                    #raise
            print
            plug.postUpload()
        except Exception, e:
            self.log.write(e)
            raise        
    
    def uploadData(self, table, data):
        """upload a data from table, where data is a dict representing a result from table"""
        # meta info
        datadict = {}
        datadict['table']=table
        datadict['method'] = 'upload'
        datadict['data'] = data
        # data
        root = self.xmlmgr.dictToXML(datadict, head='root')
        xmlstring = ElementTree.tostring(root, encoding='utf8')
                
        synctime = self.service.upload(xmlstring)
        
        if table in conf.tables_with_file:
            self.uploadFile(data['file'])
        
        self.db.setAsSynced(table, conf.keys[table], data[conf.keys[table]], synctime)    
        
    
    def downloadTable(self, table):
        try:
            self.log.write('download: %s' % (table,))
            plug = self.getPlugin(table)
            plug.preDownload()
            keytosync = self.service.getKeysToSync(table, self.last_sync_time, self.next_sync_time)
            if not keytosync:
                return
            keys = keytosync.split(',')
            total = len(keys)
            i = 1
            for key in keys:
                try:
                    print '\r', i, '/', total,
                    i = i + 1
                    xmlstring = self.downloadData(table, key)
                    if not xmlstring:
                        continue
                    data = self.xmlmgr.XMLToDict(xmlstring)
                    data = data['data']
                    if self.db.alreadyUpToDate(table, data):
                        continue
                    else:
                        data = plug.preDownloadData(data)
                        self.db.updateData(table, data)
                        data = plug.postDownloadData(data)
                    
                    if table in conf.tables_with_file:
                        self.downloadFile(data['file'])
                except Exception,e:
                    self.log.write(table+' '+key)
                    self.log.write(e)
                    keys.append(key)
                    time.sleep(float(5))
                    i = i - 1
            print
            plug.postDownload()
        except Exception, e:
            self.log.write(e)
            raise
        
    def getPlugin(self, table):
        try:
            plug = conf.plugins[table](self.db)
        except exceptions.KeyError, e:
            plug = plugin.PluginAbstract()
        return plug
            
    def downloadData(self, table, key):
        """download a data from the web service"""
        xmlstring = self.service.download(table, key)
        if xmlstring=='':
            return None
        else:
            if type(xmlstring)==str:
                xmlstring = xmlstring.decode('utf8')
            return xmlstring
    
    def uploadFile(self, filepath):
        try:
            if os.sep=='/':
                filepath = filepath.replace('\\', '/')
            else:
                filepath = filepath.replace('/', '\\')
            file = open(os.path.join(conf.data_dir_root, filepath), 'rb')
            filedata = file.read()
            self.service.putFile(filepath, Attachment(data=filedata))
        except exceptions.IOError, e:
            self.log.write(e)            

    def downloadFile(self, filepath):
        try:
            data = self.service.getFile(filepath)
            if data.data=='None':
                return            
            if os.sep=='/':
                filepath = filepath.replace('\\', '/')
            else:
                filepath = filepath.replace('/', '\\')
            fullpath = os.path.join(conf.data_dir_root, filepath)
            if not os.path.isdir(os.path.dirname(fullpath)):
                os.makedirs(os.path.dirname(fullpath))
            file = open(fullpath, 'wb')
            file.write(data.data)
            file.close()
        except Exception, e:
            self.log.write(e)
            raise

def dobackup():
    import conf
    if not os.path.isdir('mysqlbackup'):
        os.mkdir('mysqlbackup')
    cmd = 'mysqldump -u%s -p%s --host=%s --port=3306 %s > %s' \
              % (conf.mysql_options['user'], \
                conf.mysql_options['passwd'], \
                conf.mysql_options['host'], \
                conf.mysql_options['schema'], \
                os.path.join('mysqlbackup', time.strftime('%Y%m%d%H%M%S', time.localtime())+'.sql'))
    os.system(cmd)
    
if __name__=='__main__':    
    #s = Sync2()
    #s.uploadTable('record')
    #exit()

    i = 100
    while(True):
        try:
            i = i + 1
            import conf
            if conf.do_backup and i > 10:
                i = 0
                dobackup()
            s = Sync2()
            s.syncAll()
            print '========================================================'
            time.sleep(float(conf.sync_internal))
        except Exception, e:
            print e
            f = open('sync2error.txt', 'a')            
            print >> f, e
            f.close()
            time.sleep(float(conf.sync_internal))
