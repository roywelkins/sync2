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
basedir = 'd:\\BioVerify\\Database\\'
newbasedir = 'd:\\BioVerify\\Database\\'

db_conn = MySQLdb.connect(opts['host'], opts['user'], opts['passwd'], opts['schema'], cursorclass=MySQLdb.cursors.DictCursor)
cursor = db_conn.cursor()
cursor.execute('set names utf8')

cursor.execute('select template.*,sample.file from template left outer join sample on template.sample_id = sample.sample_id')
templates = cursor.fetchall()
cursor.execute('commit')
cursor.execute('start transaction')
i = 0
for old_template in templates:
    print '\r', i,
    i = i+1
    samplefile = old_template['sample.file']
    if not os.path.isfile(os.path.join(basedir, samplefile)):
        print samplefile + ' does not exist'
        cursor.execute('update template set valid = 0 where template_id = %s' % old_template['template_id'])
        continue
    samplepath = os.path.join(basedir, samplefile)
    oldfile = old_template['file']
    dir = oldfile[:oldfile.rfind('\\')]
    gentime = time.localtime()    
    newfile = os.path.join(dir, time.strftime('%Y-%m-%d_%H-%M-%S', gentime) + '.bi')
    newpath = os.path.join(newbasedir, newfile)
    if not os.path.isdir(os.path.dirname(newpath)):
        os.makedirs(os.path.dirname(newpath))
    newfile = newfile.replace('\\', '\\\\')
    cmd = 'Enroll.exe %s %s a output.txt' % (samplepath, newpath)
    os.system(cmd)
    sql = 'insert into template (uuid, person_id, person_uuid, class_id, class_uuid, sample_id, sample_uuid, database_id, algorithm_id, modify_time, file, valid, sync) values\
                   ("%s", %s, "%s", %s, "%s", %d, "%s", 1016, 2, "%s", "%s", %s, "%s")' %\
                   (uuid.uuid1(), old_template['person_id'], old_template['person_uuid'], old_template['class_id'], old_template['class_uuid'], old_template['sample_id'], old_template['sample_uuid'], time.strftime('%Y-%m-%d %H:%M:%S', gentime), newfile, old_template['valid'], time.strftime('%Y-%m-%d %H:%M:%S', gentime))
    cursor.execute(sql)
    cursor.execute('update template set valid = 0 where template_id = %s' % old_template['template_id'])
cursor.execute('commit')


