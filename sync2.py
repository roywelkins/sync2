#!/usr/bin/env python
"""The code that do the real things about syncing."""

import os
import suds
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import conf
from db import Sync2Db

class Sync2: 
    def __init__(self):
        try:
            self.service = suds.client.Client(conf.web_service_url).service
        except Exception, e:
            print 'info: network is not reachable'
#            raise Exception('unable to connect to service')
        try:
            self.db = Sync2Db()
        except Exception, e:
            # could not connect to mysql
            raise
        # TODO:
        self.last_sync_time = self.db.getLastSyncTime()
        self.next_sync_time = "2010-01-01 08:22:31"
        #self.next_sync_time = service.getCurrentTime()
        
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
        datas = self.db.getDatas(table, "sync is null")
        for data in datas:
            try:
                synctime = self.uploadData(table, data)
                self.db.setAsSynced(table, conf.keys[table], data[conf.keys[table]], synctime)
            except Exception, e:
                print e
    
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
            file = open(os.path.join(conf.data_dir_root, filepath))
            filedata = file.read()
            #self.service.putFile(filepath, filedata)
        except Exception, e:
            print e
    
if __name__=='__main__':
    s = Sync2()
    s.uploadTable("student_info")
    #s.syncAll()
