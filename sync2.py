#!/usr/bin/env python
"""The code that do the real things about syncing."""

import os
import suds
import conf
import MySQLdb
import MySQLdb.cursors
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

class Sync2: 
    def __init__(self):
        self.service = suds.client.Client(conf.web_service_url).service
        self.db_conn = MySQLdb.connect(conf.mysql_host, conf.mysql_user, conf.mysql_passwd, conf.mysql_schema, cursorclass=MySQLdb.cursors.DictCursor)
        cursor = self.db_conn.cursor()
        # TODO:
        cursor.execute('select create_time from class limit 1')
        self.last_sync_time = cursor.fetchone().values()[0]
        self.next_sync_time = "2010-01-01 08:22:31"
        #self.next_sync_time = service.getCurrentTime()
        
    def syncAll(self):        
        if conf.is_register_server:
            upload_tables = conf.common_upload_tables + conf.server_upload_tables
        else:
            upload_tables = list(conf.common_upload_tables)
        for tablename in upload_tables:
            self.uploadTable(tablename)
            
        if conf.is_register_server:
            download_tables = conf.common_download_tables + conf.server_download_tables
        else:
            download_tables = list(conf.common_download_tables)
        for tablename in download_tables:
            self.downloadTable(tablename)            
    
    def uploadTable(self, tableName):
        datas = self.getAllDataInTable(tableName, "sync is null")
        for data in datas:
            root = ElementTree.Element('xml_root')
            e = Element('table')
            e.text = tableName
            root.append(e)
            e = Element('method')
            e.text = 'upload'
            root.append(e)
            e.text = 'upload'
            data_element = self.dataToXML(data)
            root.append(data_element)
            xmlstring = ElementTree.tostring(root)
            #self.service.uploadXML(xmlstring)
            
            if tableName in conf.tables_with_file:
                self.uploadFile(data['file'])
            
            self.setAsSynced(tableName, conf.keys[tableName], data[conf.keys[tableName]])           
    
    def downloadTable(self, tableName):
        print 'down: ' + tableName
    
    def getAllDataInTable(self, tableName, where):
        """return a dict of the table having the where condition"""
        cursor = self.db_conn.cursor()
        cursor.execute('select * from '+tableName)
        return cursor.fetchall()
        
    def dataToXML(self, data):
        root = ElementTree.Element('data')
        for key, value in data.items():
            e = ElementTree.Element(key)
            e.text = str(value)
            root.append(e)
        return root
    
    def uploadFile(self, filepath):
        try:
            file = open(os.path.join(conf.data_dir_root, filepath))
            filedata = file.read()
            #self.service.putFile(filepath, filedata)
        except Exception, e:
            print e
        
    def setAsSynced(self, tableName, key, value):
        sql = "update %s set sync = current_timestamp where %s = %s" % (tableName, key, value)
        #cursor = self.db_conn.cursor()
        #cursor.execute(sql)

if __name__=='__main__':
    s = Sync2()
    s.syncAll()