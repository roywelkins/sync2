#!/usr/bin/env python

import MySQLdb
import MySQLdb.cursors
import time
import os
import uuid

opts = {
    'host':'localhost',
    'user':'root',
    'passwd':'root',
    'schema':'bioverify_new'
}
basedir = 'd:\\data\\'

db_conn = MySQLdb.connect(opts['host'], opts['user'], opts['passwd'], opts['schema'], cursorclass=MySQLdb.cursors.DictCursor)
cursor = db_conn.cursor()
cursor.execute('set names utf8')

cursor.execute('select * from template')
templates = cursor.fetchall()
cursor.execute('commit')
for old_template in templates:
    sample_uuid = old_template['sample_uuid']
    cursor.execute('select file from sample where uuid = "%s"' % sample_uuid)
    sample = cursor.fetchone()
    cursor.execute('commit')
    samplefile = sample['file']
    if not os.path.isfile(os.path.join(basedir, samplefile)):
        print samplefile + ' does not exist'
        continue
    oldfile = old_template['file']
    dir = oldfile[:oldfile.rfind('\\')]
    gentime = time.localtime()    
    newfile = os.path.join(dir, time.strftime('%Y-%m-%d_%H-%M-%S', gentime) + '.bmp')
    newfile = newfile.replace('\\', '\\\\')
    # TODO:
    # gen new template_file using
    # 1. sample_file
    # 2. newfile, that's the new template file
    sql = 'insert into template (uuid, person_id, person_uuid, class_id, class_uuid, sample_id, sample_uuid, database_id, algorithm_id, modify_time, file, valid, sync) values\
                   ("%s", %s, "%s", %s, "%s", %d, "%s", 1016, 2, "%s", "%s", %s, "%s")' %\
                   (uuid.uuid1(), old_template['person_id'], old_template['person_uuid'], old_template['class_id'], old_template['class_uuid'], old_template['sample_id'], old_template['sample_uuid'], time.strftime('%Y-%m-%d %H:%M:%S', gentime), newfile, old_template['valid'], time.strftime('%Y-%m-%d %H:%M:%S', gentime))
    cursor.execute(sql)
    cursor.execute('commit')
    cursor.execute('update template set valid = 0 where template_id = %s' % old_template['template_id'])


