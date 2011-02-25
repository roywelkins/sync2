#!/usr/bin/env python
# coding:utf8

import MySQLdb
import MySQLdb.cursors
import baseconf as conf
import datetime

class Db:
    """comunicate with the sql server"""

    def __init__(self, opts):
        self.opts = opts
        self.db_conn = MySQLdb.connect(opts['host'], opts['user'], opts['passwd'], opts['schema'], cursorclass=MySQLdb.cursors.DictCursor)
        cursor = self.db_conn.cursor()
        cursor.execute('set names utf8')
        cursor.close()
        self.log = None
        self.database_id = 1017
        
    def getLastSyncTime(self):
        cursor = self.db_conn.cursor()
        cursor.execute('select last_sync from database_info where database_id = %d' % self.database_id)
        t = cursor.fetchone()
        cursor.execute('commit')
        cursor.close()
        if t==None:
            self.log.write('%d database does not exist' % self.database_id)
            raise Exception('fatal error: %d database does not exist' % self.database_id)
        t = t['last_sync']
        if t==None:
            # this is the first time of running sync2
            t = datetime.datetime(2010,03,11,00,00,00)
        return t.__str__()
        
    def setLastSyncTime(self, synctime):
        self.executeSQL('update database_info set last_sync="%s" where database_id = %d' % (synctime, self.database_id))
    
    def getKeysInTableWithSyncBetween(self, table, lasttime, nexttime):
        """as the name says
        
        this method is not check due to database format not done
        """
        cursor = self.db_conn.cursor()
        #cursor.execute('start transaction')
        sql = 'select %s from %s where sync between "%s" and "%s"' % (conf.keys[table], table, lasttime, nexttime)
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.execute('commit')
        cursor.close()
        re = [v[conf.keys[table]] for v in results]
        return re             
  

    def getDatas(self, table, where=None):
        """return a dict of the table having the where condition"""
        cursor = self.db_conn.cursor()
        #cursor.execute('start transaction')
        sql = 'select * from '+table
        if where:
            sql = sql + ' where '+where
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.execute('commit')
        cursor.close()
        return result
    
    def getData(self, table, where=None):
        """return a dict of the table having the where condition"""
        cursor = self.db_conn.cursor()
        #cursor.execute('start transaction')
        sql = 'select * from '+table
        if where:
            sql = sql + ' where '+where
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.execute('commit')
        cursor.close()
        return result
    
    def setAsSynced(self, table, key, value, synctime):
        """set a record as synced at synctime where having key=value(such as uuid=xxxxxxxx)"""
        sql = "update %s set sync = '%s' where %s = '%s'" % (table, synctime, key, value)
        self.executeSQL(sql)

    def alreadyUpToDate(self, table, data):
        """test if data is up to date"""
        cursor = self.db_conn.cursor()
        #cursor.execute('start transaction')
        sql = 'select %s, sync from %s where %s="%s"' % (conf.keys[table], table, conf.keys[table], data[conf.keys[table]])
        cursor.execute(sql)
        d = cursor.fetchone()
        cursor.execute('commit')
        cursor.close()
        if not d:
            return False
        sync = d['sync'].__str__()
        if sync==data['sync'] or sync == 'None':
            return True
        return False

    def updateData(self, table, data):
        """update table with data
        
        if the key of data already exists, delete the old data and insert the new one
        """
        #好像有潜在的造成某一行锁住，所有操作都不能提交的可能
        key = data[conf.keys[table]]
        if self.isNull(key):
            return
        if self.keyAlreadyExists(table, key):
            self.deleteData(table, key)
        self.insertData(table, data)

    def deleteData(self, table, key):
        """delete a data from table with key"""
        sql = 'delete from %s where %s = "%s"' % (table, conf.keys[table], key)
        self.executeSQL(sql)

    def insertData(self, table, data):
        """insert a data into table
        
        it should not be called directly, instead, use updateData
        """
        new = {}
        for item in data.items():
            if table in conf.field_exclude.keys() and item[0] in conf.field_exclude[table]:
                pass
            elif self.isNull(item[1]):
                pass
                #new[item[0]] = 'NULL'
            elif type(item[1])==str:
                new[item[0]] = item[1].decode('utf8')
            else:
                new[item[0]] = unicode(item[1])            
            if item[0]=='file':
                new[item[0]] = new[item[0]].replace('\\', '\\\\')                
        sql = 'insert into %s (%s) values ("%s")' % (table, ','.join(new.keys()), '","'.join(new.values()))
        self.executeSQL(sql.encode('utf8'))
            
    def keyAlreadyExists(self, table, key):
        """check if key already exists in table"""
        cursor = self.db_conn.cursor()
        #cursor.execute('start transaction')
        sql = 'select * from %s where %s = "%s"' % (table, conf.keys[table], key)
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.execute('commit')
        cursor.close()
        if result:
            return True
        else:
            return False
        
    def recordDeduplicate(self):
        cursor = self.db_conn.cursor()
        cursor.execute('select person_id,date(time),count(*) from record where result=22 group by person_id,date(time) having count(*)>1')
        records = cursor.fetchall()
        cursor.execute('commit')
        cursor.close()
        for record in records:
            sql = 'update record set result = 5 where person_id = "%s" and date(time) = "%s" and result = 22 order by time desc limit %d' % (record['person_id'], record['date(time)'], record['count(*)']-1)
            self.executeSQL(sql)
        
    def genResult(self):
        # 这不靠谱，太慢，要改成插件形式
        self.executeSQL('insert into result_info (person_id,person_uuid,sync, extra_mor) select person_id,person_uuid,current_timestamp,1 from person_extra where registered = 1 and person_id not in (select distinct(person_id) from result_info)')
        #self.executeSQL('update result_info set sync=current_timestamp, total_mor = (select count(*) from record where person_id=result_info.person_id and result=21)')
        #self.executeSQL('update result_info set sync=current_timestamp, total_eve = (select count(*) from record where person_id=result_info.person_id and result=22)')
    
    def genOneResult(self, person_id, person_uuid):
        result = self.getOneResult('select * from result_info where person_id = "%s"' % person_id)
        if not result:
            self.executeSQL('insert into result_info (person_id, person_uuid, sync, extra_mor) values ("%s", "%s", current_timestamp, 1)' % (person_id, person_uuid))        
        
    def executeSQL(self, sql):
        cursor = self.db_conn.cursor()
        #cursor.execute('start transaction')        
        cursor.execute(sql+';commit;')
        cursor.close()
        
    def getAllResult(self, sql):
        cursor = self.db_conn.cursor()
        #cursor.execute('start transaction')
        cursor.execute('commit')
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.execute('commit')
        cursor.close()
        return results
    
    def getOneResult(self, sql):
        cursor = self.db_conn.cursor()
        #cursor.execute('start transaction')
        cursor.execute('commit')
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.execute('commit')
        cursor.close()
        return result
    
    def isNull(self, obj):
        return obj=='None' or obj==None or obj=='NULL' or obj=='null'
            
            
if __name__=='__main__':
    import conf
    import logger
    d = Db(conf.mysql_options)    
    d.log = logger.Logger('logs', 'dbtest.txt')
    #cursor = d.db_conn.cursor()
    #cursor.execute('select person_uuid from person_extra where sync between "2010-03-10 21:38:40" and "2010-03-10 22:23:42" limit 500')
    #cursor.execute('commit')
    #cursor.execute('select person_uuid from person_extra where sync between "2010-03-10 21:38:40" and "2010-03-10 22:23:42" limit 500')
    #cursor.execute('select card_no from card_info where sync between "2010-03-10 21:38:40" and "2010-03-10 22:23:43" limit 500')
    #cursor.execute('commit')
    exit()
    for data in d.getDatas('student_info', 'sync is null'):
        if not d.alreadyUpToDate('student_info', data):
            print 'shit'
