#!/usr/bin/env python
#coding:utf8

import sys
import os
sys.path.append('../..')
from sync2 import db

d = db.Db({'user':'root',\
           'passwd':'root',\
           'schema':'bioverify_new',\
           'host':'localhost'})

d = db.Db({'user':'pe',\
           'passwd':'pebioverify',\
           'schema':'bioverify_new',\
           'host':'162.105.81.242'})


#d.executeSQL('alter table person_info change student_id `student_id` char(10) DEFAULT NULL;')
#d.executeSQL('alter table card_info change student_id `student_id` char(10) DEFAULT NULL;')
#alter table student_tc change student_id `student_id` char(10) DEFAULT NULL;

#files = ['07', '08', '09', '10', '09.TXT']
#files = ['10000.TXT', '10103.TXT']
files = ['aa.txt']

for filename in files:
    filename = os.path.join('.', 'files', '2010autumn', filename)
    f = open(filename, 'r')
    data = f.read().decode('gbk')
    data = data.split('\n')
    for line in data[1:]:
        #print line
        line = line.rstrip('\n')
        (card_no, name, student_id) = line.split(',')
        if len(student_id)>10 or len(student_id)<8:
            continue        
        old = d.getOneResult('select * from card_info where card_no = "%s"' % card_no)
        if old and old['student_id']!=student_id:
            print line, old['student_id']
            d.executeSQL('delete from card_info where card_no = "%s"' % card_no)
            
        person = d.getOneResult('select * from person_info where student_id = "%s"' % student_id)
        if not person:
            print 'new person: ', student_id
            sql = ('insert into person_info (uuid,student_id,sync, name) values (uuid(), "%s", current_timestamp, "%s")' % (student_id, name)).encode('utf8');
            d.executeSQL(sql)
            person = d.getOneResult('select * from person_info where student_id = "%s"' % student_id)
        if not old:
            print 'new card: ', card_no
            sql = 'insert into card_info (card_no, person_id, person_uuid, student_id, sync) values ("%s", "%s", "%s", "%s", current_timestamp)' \
                   % (card_no, person['person_id'], person['uuid'], student_id)
            d.executeSQL(sql)
        #sql = ('update person_info set name="%s",sync=current_timestamp where person_id = %d' % (name, person['person_id'])).encode('utf8')
        #d.executeSQL(sql)

    continue    


# 修复性工作，不用做        
    card_infos = d.getAllResult('select * from card_info where person_id is null group by student_id')
    for card_info in card_infos:       
        sql = 'insert into person_info (uuid,student_id,sync) values (uuid(), "%s", current_timestamp)' % card_info['student_id']
        d.executeSQL(sql)
        person = d.getOneResult('select * from person_info where student_id = "%s"' % card_info['student_id'])
        sql = 'update card_info set person_id = "%s", person_uuid = "%s",sync=current_timestamp where card_no = "%s"' % (person['person_id'], person['uuid'], card_info['card_no'])
        d.executeSQL(sql)
