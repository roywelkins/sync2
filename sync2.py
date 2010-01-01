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
        cursor.execute('set names utf8')
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
        for table in upload_tables:
            self.uploadTable(table)
            
        if conf.is_register_server:
            download_tables = conf.common_download_tables + conf.server_download_tables
        else:
            download_tables = list(conf.common_download_tables)
        for table in download_tables:
            self.downloadTable(table)            
    
    def uploadTable(self, table):
        datas = self.getAllDataInTable(table, "sync is null")
        for data in datas:
            self.uploadData(table, data)
    
    def uploadData(self, table, data):
        """upload a data from table, where data is a dict representing a result from table"""
        root = ElementTree.Element('xml_root')
        e = Element('table')
        e.text = table
        root.append(e)
        e = Element('method')
        e.text = 'upload'
        root.append(e)
        e.text = 'upload'
        data_element = self.dataToXML(data)
        root.append(data_element)
        xmlstring = ElementTree.tostring(root, encoding='utf8')
        #self.service.uploadXML(xmlstring)
        
        if table in conf.tables_with_file:
            self.uploadFile(data['file'])
        
        self.setAsSynced(table, conf.keys[table], data[conf.keys[table]])
    
    def downloadTable(self, table):
        print 'down: ' + table        
        
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
    
        
    # about the database
    # maybe I should take it out as another class
    def getAllDataInTable(self, table, where):
        """return a dict of the table having the where condition"""
        cursor = self.db_conn.cursor()
        cursor.execute('select * from '+table)
        return cursor.fetchall()
        
    def setAsSynced(self, table, key, value):
        sql = "update %s set sync = current_timestamp where %s = %s" % (table, key, value)
        #cursor = self.db_conn.cursor()
        #cursor.execute(sql)

if __name__=='__main__':
    s = Sync2()
    s.uploadTable("student_info")
    #s.syncAll()