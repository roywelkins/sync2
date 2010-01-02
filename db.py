#!/usr/bin/env python

import MySQLdb
import MySQLdb.cursors
import conf

class Sync2Db:
    """comunicate with the sql server"""

    def __init__(self):
        db_conn = MySQLdb.connect(conf.mysql_host, conf.mysql_user, conf.mysql_passwd, conf.mysql_schema, cursorclass=MySQLdb.cursors.DictCursor)
        cursor = db_conn.cursor()
        cursor.execute('set names utf8')
        self.db_conn = db_conn

    def getLastSyncTime(self):
        return "2009-01-01 01:01:01"

    def getDatas(self, table, where):
        """return a dict of the table having the where condition"""
        cursor = self.db_conn.cursor()
        cursor.execute('select * from '+table)
        return cursor.fetchall()
        
    def setAsSynced(self, table, key, value, synctime):
        """set a record as synced at synctime where having key=value(such as uuid=xxxxxxxx)"""
        sql = "update %s set sync = %s where %s = %s" % (table, synctime, key, value)
        #cursor = self.db_conn.cursor()
        #cursor.execute(sql)

    def alreadyUpToDate(self, table, data):
        """test if data is up to date"""
        cursor = self.db_conn.cursor()
        sql = "select %s, sync from %s" % (conf.keys[table], table)
        try:
#TODO
#            cursor.execute(sql)
            d = cursor.fetchone()
            if not d:
                return False
            if d[conf.keys[table]]==data[conf.keys[table]] \
                    and d['sync']==data['sync']:
                return True
            return False
        except Exception, e:
            print e

    def updateData(self, table, data):
        key = data[conf.keys[table]]
        cursor = self.db_conn.cursor()
        if self.keyAlreadyExists(table, key):
            self.deleteData(table, key)
        self.insertData(table, data)

    def deleteData(self, table, key):
        cursor = self.db_conn.cursor()
        sql = 'delete from %s where %s = %s' % (table, conf.keys[table], key)
        cursor.execute(sql)

    def insertData(self, table, data):
        pass
