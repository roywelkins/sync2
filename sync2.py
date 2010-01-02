#!/usr/bin/env python
"""The code that do the real things about syncing."""

import os
import traceback
import time
import soaplib.client
from soaplib.serializers.binary import Attachment
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import conf
from db import Sync2Db
from sync2webservice import Sync2WebService
from logger import Logger

class Sync2: 
    def __init__(self):
        self.log = Logger('sync2.log.'+time.strftime('%Y%m%d', time.localtime()))
        try:
            self.service = soaplib.client.make_service_client(conf.web_service_url, Sync2WebService())
            self.next_sync_time = self.service.getCurrentTime()
        except Exception:
            pass
#            raise TODO
        try:
            self.db = Sync2Db(conf.mysql_options)
        except Exception, e:
            raise
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
                    print e
        except Exception, e:
            traceback.print_exc(file=self.log.file)
    
    def uploadData(self, table, data):
        """upload a data from table, where data is a dict representing a result from table"""
        # meta info
        root = ElementTree.Element('xml_root')
        e = Element('table')
        e.text = table
        root.append(e)
        e = Element('method')
        e.text = 'upload'
        root.append(e)
        # data
        data_element = self.dataToXML(data)
        root.append(data_element)
        xmlstring = ElementTree.tostring(root, encoding='utf8')
        #self.service.uploadXML(xmlstring)
        
        if table in conf.tables_with_file:
            self.uploadFile(data['file'])
        
    
    def downloadTable(self, table):
        pass
        keys = self.service.getKeysToBeSync(table, self.last_sync_time, self.next_sync_time)
        for key in keys:
            xmlstring = downloadData(table, key)            
            data = xmlToData(xmlstring)
            if self.db.alreadyUpToDate(table, data):
                continue
            else:
                self.db.updateData(table, data)

    def dataToXML(self, data):
        root = ElementTree.Element('data')
        for key, value in data.items():
            e = ElementTree.Element(key)
            if type(value)==str:
                e.text = value.decode('utf8')
            else:
                e.text = unicode(value)
            root.append(e)
        return root
    
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
            print e

    def downloadFile(self, filepath):
        try:
            data = self.service.getFile(filepath)
            file = open(os.path.join(conf.data_dir_root, filepath), 'wb')
            file.write(data.data)
            file.close()
        except Exception, e:
            print e

    
if __name__=='__main__':
    s = Sync2()
    s.uploadTable('student_info')
    #s.syncAll()
