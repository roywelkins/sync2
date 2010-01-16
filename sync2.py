#!/usr/bin/env python
"""The code that controls the syncer workflow"""

import os
import traceback
import time
import soaplib.client
from soaplib.serializers.binary import Attachment
from xml.etree import ElementTree
#from xml.etree.ElementTree import Element

import conf
import db
import xmlmgr
from sync2webservice import Sync2WebService
import logger

class Sync2: 
    def __init__(self):
        self.log = logger.Logger(conf.logdir, 'sync2.log.'+time.strftime('%Y%m%d', time.localtime())+'.txt')
        self.xmlmgr = xmlmgr.XMLManager()
        try:
            self.service = soaplib.client.make_service_client(conf.web_service_url, Sync2WebService())
            #self.service = Sync2WebService()
            self.log.write('checking connection with url: ' + conf.web_service_url)
            self.next_sync_time = self.service.getCurrentTime()
            self.log.write('server time: ' + self.next_sync_time)
            exit()
        except Exception, e:
            self.log.write(e)
#            raise TODO
        try:
            self.db = db.Db(conf.mysql_options)
            self.db.log = self.log
        except Exception, e:
            self.log.write(e)
        # TODO:
        self.last_sync_time = self.db.getLastSyncTime()        
        
    def syncAll(self):        
        if conf.is_register_server:
            upload_tables = conf.common_upload_tables + conf.server_upload_tables
        else:
            upload_tables = list(conf.common_upload_tables)
        for table in upload_tables:
            self.uploadTable(table)
            
        if conf.is_register_server:
            download_tables = conf.common_download_tables + conf.server_download_tables
        else:
            download_tables = list(conf.common_download_tables)
        for table in download_tables:
            self.downloadTable(table)            
    
    def uploadTable(self, table):
        try:
            datas = self.db.getDatas(table, "sync is null")
            for data in datas:
                try:
                    synctime = self.uploadData(table, data)
                    self.db.setAsSynced(table, conf.keys[table], data[conf.keys[table]], synctime)
                except Exception, e:
                    self.log.write(e)
        except Exception, e:
            traceback.print_exc(file=self.log.file)
    
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
        
        #self.service.uploadData(xmlstring)
        
        if table in conf.tables_with_file:
            self.uploadFile(data['file'])
        
    
    def downloadTable(self, table):
        try:
            keys = self.service.getKeysToBeSync(table, self.last_sync_time, self.next_sync_time).split(',')
            if not keys:
                return
            for key in keys:
                xmlstring = downloadData(table, key)
                data = xmlToData(xmlstring)
                if self.db.alreadyUpToDate(table, data):
                    continue
                else:
                    self.db.updateData(table, data)
                
                if table in conf.tables_with_file:
                    self.downloadFile(self, data['file'])
        except Exception, e:
            self.log.write(e)
    
    def uploadFile(self, filepath):
        try:
            if os.sep=='/':
                filepath = filepath.replace('\\', '/')
            else:
                filepath = filepath.replace('/', '\\')
            file = open(os.path.join(conf.data_dir_root, filepath), 'rb')
            filedata = file.read()
            self.service.putFile(filepath, Attachment(data=filedata))
        except Exception, e:
            self.log.write(e)

    def downloadFile(self, filepath):
        try:            
            data = self.service.getFile(filepath)
            if os.sep=='/':
                filepath = filepath.replace('\\', '/')
            else:
                filepath = filepath.replace('/', '\\')
            file = open(os.path.join(conf.data_dir_root, filepath), 'wb')
            file.write(data.data)
            file.close()
        except Exception, e:
            self.log.write(e)

    
if __name__=='__main__':
    s = Sync2()
    s.uploadTable('student_info')
    #s.syncAll()
