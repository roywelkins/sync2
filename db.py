#!/usr/bin/env python

import MySQLdb
import MySQLdb.cursors
import conf

class Db:
    """comunicate with the sql server"""

    def __init__(self, opts):
        db_conn = MySQLdb.connect(opts['host'], opts['user'], opts['passwd'], opts['schema'], cursorclass=MySQLdb.cursors.DictCursor)
        cursor = db_conn.cursor()
        cursor.execute('set names utf8')
        self.db_conn = db_conn
        self.log = None
        self.database_id = 1016
        

    def getLastSyncTime(self):
        try:
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
            return t
        except Exception, e:
            sele.log.write(e)
            return None
    
    def getKeysInTableWithSyncBetween(self, table, lasttime, nexttime):
        """as the name says
        
        this method is not check due to database format not done
        """
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('start transaction')
            sql = 'select %s from %s where sync between %s and %s limit 500' % (conf.keys[table], table, lasttime, nexttime)
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.execute('commit')
            if not results:
                return None
            results = [v[0] for v in results]
            return ','.join(results)                
        except Exception, e:
            self.log.write(e)
            return None        

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
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('start transaction')
            sql = "update %s set sync = '%s' where %s = '%s'" % (table, synctime, key, value)        
            cursor.execute(sql)
            cursor.execute('commit')
        except Exception, e:
            self.log.write(e)

    def alreadyUpToDate(self, table, data):
        """test if data is up to date"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('start transaction')
            sql = 'select %s, sync from %s where %s="%s"' % (conf.keys[table], table, conf.keys[table], (data[conf.keys[table]]))
            cursor.execute(sql)
            d = cursor.fetchone()
            cursor.execute('commit')
            if not d:
                return False
            if d[conf.keys[table]]==data[conf.keys[table]] \
                    and d['sync']==data['sync']:
                return True
            return False
        except Exception, e:
            self.log.write(e)

    def updateData(self, table, data):
        """update table with data
        
        if the key of data already exists, delete the old data and insert the new one
        """
        key = data[conf.keys[table]]        
        if self.keyAlreadyExists(table, key):
            self.deleteData(table, key)
        self.insertData(table, data)

    def deleteData(self, table, key):
        """delete a data from table with key"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('start transaction')
            sql = 'delete from %s where %s = "%s"' % (table, conf.keys[table], key)
            cursor.execute(sql)
            cursor.execute('commit')
        except Exception, e:
            self.log.write(e)

    def insertData(self, table, data):
        """insert a data into table
        
        it should not be called directly, instead, use updateData
        """
        try:
            new = {}
            for item in data.items():
                if item[1]=='None' or item[1]==None or item[1]=='NULL' or item[1]=='null':
                    pass
                    #new[item[0]] = 'NULL'
                elif type(item[1])==str:
                    new[item[0]] = item[1].decode('utf8')
                else:
                    new[item[0]] = unicode(item[1])
            cursor = self.db_conn.cursor()
            cursor.execute('start transaction')
            sql = 'insert into %s (%s) values ("%s")' % (table, ','.join(new.keys()), '","'.join(new.values()))
            cursor.execute(sql.encode('utf8'))
            cursor.execute('commit')
        except Exception, e:
            self.log.write(e)
            
    def keyAlreadyExists(self, table, key):
        """check if key already exists in table"""
        try:
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
        except Exception, e:
            self.log.write(e)    
            
            
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
