#!/usr/bin/env python
#coding:utf8

import MySQLdb

conn = MySQLdb.connect('localhost', 'root', 'root', 'bioverify_new')
cur = conn.cursor()
cur.execute('set names utf8')

for i in range(1, 10):
    sql = 'insert into place_info (info, mor_begin, mor_end, eve_begin, eve_end, wd_mor_begin, wd_mor_end, wd_eve_begin, wd_eve_end, min_internal, max_internal) \
            values \
            ("第一体育馆_%d", "2008-01-01 07:00:00", "2008-01-01 08:30:00", "2008-01-01 16:00:00", "2008-01-01 21:30:00", "2008-01-01 07:00:00", "2008-01-01 09:00:00", "2008-01-01 09:00:00", "2008-01-01 21:30:00", 30, 240)' \
            % i
    print sql , ';'
    
for i in range(1, 3):
    sql = 'insert into place_info (info, mor_begin, mor_end, eve_begin, eve_end, wd_mor_begin, wd_mor_end, wd_eve_begin, wd_eve_end, min_internal, max_internal) \
            values \
            ("五四体育馆_%d", "2008-01-01 00:00:00", "2008-01-01 00:00:00", "2008-01-01 16:00:00", "2008-01-01 21:30:00", "2008-01-01 00:00:00", "2008-01-01 00:00:00", "2008-01-01 09:00:00", "2008-01-01 21:30:00", 30, 240)' \
            % i
    print sql , ';'
    