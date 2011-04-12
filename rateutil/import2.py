#coding:gbk
# create 1003 test (RATE refine)
# 100 classes each 5 samples
# class内的sample两两匹配
# 每个sample都和其他class的第一个匹配一次

import MySQLdb
import MySQLdb.cursors
import os

# config
for dbid in range(2009, 2012):
########
    
    conn = MySQLdb.connect('localhost', 'root', 'root', 'rate')#, cursorclass=MySQLdb.cursors.DictCursor)
    cursor = conn.cursor()
    
    f = open('1003_%d.txt' % dbid, 'w')
    cids = []
    samples = {}
    sql = 'select class_id from classes where database_id = %d order by rand() limit 100' % dbid
    cursor.execute(sql)
    for cid in cursor.fetchall():
        cid = cid[0]
        cids.append(cid)
        samples[cid] = []
        sql = 'select sample_id, file from samples where class_id = %d order by rand() limit 5' % cid
        c2 = conn.cursor()
        c2.execute(sql)
        for s in c2.fetchall():
            samples[cid].append(s)
            
    for cid in cids:
        for s in samples[cid]:
            #类内
            (sid, sf) = s
            print>>f, 'E %d %d %s' % (dbid, cid, sid)
            print>>f, sf
            for s2 in samples[cid][samples[cid].index(s)+1:]:
                (sid2, sf2) = s2
                print>>f, 'M %d %d %d %d %d %d' % (dbid, cid, sid, dbid, cid, sid2)
                print>>f, sf2
                
            #类间
            if samples[cid].index(s)!=0:
                continue
            for cid2 in cids[cids.index(cid)+1:]:
                (sid2, sf2) = samples[cid2][0]
                print>>f, 'M %d %d %d %d %d %d' % (dbid, cid, sid, dbid, cid2, sid2)
                print>>f, sf2
    f.close()
    
    f = open('1003_%d.txt' % dbid, 'r')
    c = f.readlines()
    f.close()
    f = open('1003_%d.txt' % dbid, 'w')
    print>>f, len(c)/2
    f.writelines(c)
