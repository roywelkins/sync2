#!/usr/bin/env python
# coding:utf8

import MySQLdb
import MySQLdb.cursors
import conf

class Db:
    """comunicate with the sql server"""

    def __init__(self, opts):
        self.opts = opts
        self.db_conn = MySQLdb.connect(opts['host'], opts['user'], opts['passwd'], opts['schema'], cursorclass=MySQLdb.cursors.DictCursor)
        cursor = self.db_conn.cursor()
        cursor.execute('set names utf8')
        self.log = None
        self.database_id = 1016
        
    def reconnect(self):        
        if not self.db_conn.open:
            print 'reconnect'
            opts = self.opts
            self.db_conn = MySQLdb.connect(opts['host'], opts['user'], opts['passwd'], opts['schema'], cursorclass=MySQLdb.cursors.DictCursor)        

    def getLastSyncTime(self):
        cursor = self.db_conn.cursor()
        cursor.execute('select last_sync from database_info where database_id = %d' % self.database_id)
        t = cursor.fetchone()
        if t==None:
            self.log.write('%d database does not exist' % self.database_id)
            raise Exception('fatal error: %d database does not exist' % self.database_id)
        t = t['last_sync']
        if t==None:
            # this is the first time of running sync2
            import datetime
            t = datetime.datetime(2000,01,01,01,01,01)
        return t.__str__()
    
    def getKeysInTableWithSyncBetween(self, table, lasttime, nexttime):
        """as the name says
        
        this method is not check due to database format not done
        """
        cursor = self.db_conn.cursor()
        cursor.execute('start transaction')
        sql = 'select %s from %s where sync between "%s" and "%s" limit 500' % (conf.keys[table], table, lasttime, nexttime)
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.execute('commit')
        re = [v[conf.keys[table]] for v in results]
        return re             
  

    def getDatas(self, table, where=None):
        """return a dict of the table having the where condition"""
        cursor = self.db_conn.cursor()
        cursor.execute('start transaction')
        sql = 'select * from '+table
        if where:
            sql = sql + ' where '+where
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.execute('commit')
        return result
        
    def setAsSynced(self, table, key, value, synctime):
        """set a record as synced at synctime where having key=value(such as uuid=xxxxxxxx)"""
        cursor = self.db_conn.cursor()
        cursor.execute('start transaction')
        sql = "update %s set sync = '%s' where %s = '%s'" % (table, synctime, key, value)
        cursor.execute(sql)
        cursor.execute('commit')

    def alreadyUpToDate(self, table, data):
        """test if data is up to date"""
        cursor = self.db_conn.cursor()
        cursor.execute('start transaction')
        sql = 'select %s, sync from %s where %s="%s"' % (conf.keys[table], table, conf.keys[table], data[conf.keys[table]])
        cursor.execute(sql)
        d = cursor.fetchone()
        cursor.execute('commit')
        if not d:
            return False
        sync = d['sync'].__str__()
        if sync==data['sync']:
            return True
        return False

    def updateData(self, table, data):
        """update table with data
        
        if the key of data already exists, delete the old data and insert the new one
        """
        #好像有潜在的造成某一行锁住，所有操作都不能提交的可能
        key = data[conf.keys[table]]        
        if self.keyAlreadyExists(table, key):
            self.deleteData(table, key)
        self.insertData(table, data)

    def deleteData(self, table, key):
        """delete a data from table with key"""
        cursor = self.db_conn.cursor()
        cursor.execute('start transaction')
        sql = 'delete from %s where %s = "%s"' % (table, conf.keys[table], key)
        cursor.execute(sql)
        cursor.execute('commit')

    def insertData(self, table, data):
        """insert a data into table
        
        it should not be called directly, instead, use updateData
        """
        new = {}
        for item in data.items():
            if table in conf.field_exclude.keys() and item[0] in conf.field_exclude[table]:
                pass
            elif item[1]=='None' or item[1]==None or item[1]=='NULL' or item[1]=='null':
                pass
                #new[item[0]] = 'NULL'
            elif type(item[1])==str:
                new[item[0]] = item[1].decode('utf8')
            else:
                new[item[0]] = unicode(item[1])            
            if item[0]=='file':
                new[item[0]] = new[item[0]].replace('\\', '\\\\')
                
        cursor = self.db_conn.cursor()
        cursor.execute('start transaction')
        sql = 'insert into %s (%s) values ("%s")' % (table, ','.join(new.keys()), '","'.join(new.values()))
        cursor.execute(sql.encode('utf8'))
        cursor.execute('commit')
            
    def keyAlreadyExists(self, table, key):
        """check if key already exists in table"""
        cursor = self.db_conn.cursor()
        cursor.execute('start transaction')
        sql = 'select * from %s where %s = "%s"' % (table, conf.keys[table], key)            
        cursor.execute(sql)            
        result = cursor.fetchone()
        cursor.execute('commit')
        if result:
            return True
        else:
            return False
        
    def executeSQL(self, sql):
        cursor = self.db_conn.cursor()
        cursor.execute('start transaction')
        cursor.execute(sql)
        cursor.execute('commit')
            
            
if __name__=='__main__':
    import conf
    import logger
    d = Db(conf.mysql_options)    
    d.log = logger.Logger('logs', 'dbtest.txt')
    d.getLastSyncTime()
    exit()
    for data in d.getDatas('student_info', 'sync is null'):
        if not d.alreadyUpToDate('student_info', data):
            print 'shit'
