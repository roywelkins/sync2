#!/usr/bin/env python
#coding:utf8

import sys
sys.path.append('../..')
from sync2 import db

d = db.Db({'user':'root',\
           'passwd':'root',\
           'schema':'bioverify_new',\
           'host':'localhost'})

# 特殊情况，这个卡跟以往的数据有冲突
d.executeSQL('delete from card_info where card_no = "%s"' % "2898134614")

f = open(u'files/校园卡20100312.csv')
for line in f.readlines():
    (card_no, student_id) = line.rstrip('\n').split(',')
    old = d.getOneResult('select * from card_info where card_no = "%s"' % card_no)
    if old:
        continue
    person = d.getOneResult('select * from person_info where student_id = "%s"' % student_id)
    if not person:
        sql = 'insert into person_info (uuid,student_id,sync) values (uuid(), "%s", current_timestamp)' % student_id
        d.executeSQL(sql)
        person = d.getOneResult('select * from person_info where student_id = "%s"' % student_id)
    sql = 'insert into card_info (card_no, person_id, person_uuid, student_id, sync) values ("%s", "%s", "%s", "%s", current_timestamp)' \
           % (card_no, person['person_id'], person['uuid'], student_id)
    d.executeSQL(sql)
    
card_infos = d.getAllResult('select * from card_info where person_id is null group by student_id')
for card_info in card_infos:
    sql = 'insert into person_info (uuid,student_id,sync) values (uuid(), "%s", current_timestamp)' % card_info['student_id']
    d.executeSQL(sql)
    person = d.getOneResult('select * from person_info where student_id = "%s"' % card_info['student_id'])
    sql = 'update card_info set person_id = "%s", person_uuid = "%s",sync=current_timestamp where card_no = "%s"' % (person['person_id'], person['uuid'], card_info['card_no'])
    d.executeSQL(sql)
