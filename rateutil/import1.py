#coding:gbk
# 给张老师做的几个

import os
import MySQLdb

for dbid in range(2009, 2012):

    # global db connection
    conn = MySQLdb.Connect("localhost", "root", "root", "rate")
    cur = conn.cursor()
    
    rootdir = "D:\\Work\\temp\\1020\\"
    
    subdir = rootdir + str(dbid) + "\\"
    
    # create the database_info
    sql = 'delete from database_info where database_id = %d' % dbid
    cur.execute(sql)
    sql = 'insert into database_info (database_id, uuid, name, type, create_time, root_dir, info, deleted) values (%d, uuid(), "%d for Mr. Zhang", 5, current_timestamp, "%d", "", current_timestamp)' % (dbid, dbid, dbid)
    cur.execute(sql)
    cur.execute('commit')
    
    # search the dir and create classes and samples
    for d in os.listdir(subdir):
        sql = 'select max(class_id) from classes'
        cur.execute(sql)
        cid = int(cur.fetchone()[0]) + 1
        sql = 'insert into classes (class_id, uuid, database_id, info, creater, name, type, create_time) values (%d, uuid(), %d, "created for Mr.Zhang", "yyk", "unnamed", 5, current_timestamp)' % (cid, dbid)
        cur.execute(sql)
        cur.execute('commit')
    
        for s in os.listdir(subdir+d):
            sql = 'select max(sample_id) from samples'
            cur.execute(sql)
            sid = int(cur.fetchone()[0]) + 1
            filepath = str(dbid)+"\\"+d+"\\"+s
            filepath = filepath.replace('\\', '\\\\')
            sql = 'insert into samples (sample_id, uuid, class_id, database_id, type, create_time, file, info, creater, quality) values ' \
            + '(%d, uuid(), %d, %d, 5, current_timestamp, "%s", "created for Mr. Zhang", "yyk", 1)' \
                % (sid, cid, dbid, filepath)
            cur.execute(sql)
        cur.execute('commit')
