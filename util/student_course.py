#!/usr/bin/env python
#coding:utf8

import sys
sys.path.append('../..')
from sync2 import db

#d = db.Db({'user':'root',\
#           'passwd':'root',\
#           'schema':'bioverify_new',\
#           'host':'localhost'})

d = db.Db({'user':'pe',\
           'passwd':'pebioverify',\
           'schema':'bioverify_new',\
           'host':'162.105.81.242'})

f = open(u'files/2011spring/1.csv')
data = f.read().decode('gbk')
data = data.split('\n')

#d.executeSQL('alter table teacher_info change teacher_id teacher_id char(15)')
#d.executeSQL('alter table teacher_course change teacher_id teacher_id char(15)')
#try:
#    d.executeSQL('describe student_tc')
#except:
#    d.executeSQL('create table student_tc (student_id char(8) not null,tc_id int unsigned not null)')
for line in data[1:-1]:
    if len(line)==0:
        continue
    (s_id,s_name,gender,dept_id,course_id,course_name,class_no,t_id,t_name) = line.split(',')
    gender = int(gender)
    if len(str(t_id))==7:
        t_id = '000' + t_id
    if len(s_id)==6:
        s_id = '00'+s_id

    if gender == 1:
        gender = 'M'
    else:
        gender = 'F'
    person = d.getOneResult('select * from person_info where student_id = "%s"' % s_id)
    if not person:
        print s_id
        continue

    
    d.executeSQL(('update person_info set sex="%s",department_no="%s",name="%s" where person_id = "%s"' % (gender,dept_id,s_name,person['person_id'])).encode('utf8'))
    
    #teacher_info
    teacher = d.getOneResult('select * from teacher_info where teacher_id = "%s"' % t_id)
    if not teacher:
        print t_id
        d.executeSQL(('insert into teacher_info (teacher_id, name) values ("%s", "%s")' % (t_id, t_name)).encode('utf8'))
    
    #course_info
    course = d.getOneResult('select * from course_info where course_no = "%s"' % course_id)
    if not course:
        print course_id
        d.executeSQL(('insert into course_info (course_no, course_name) values ("%s", "%s")' % (course_id, course_name)).encode('utf8'))
    
    #teacher_course
    tc = d.getOneResult('select * from teacher_course where teacher_id = "%s" and course_id = "%s" and class_no = "%s"' % (t_id, course_id, class_no))
    if not tc:        
        d.executeSQL('insert into teacher_course (teacher_id, course_id, year, term, class_no) values ("%s","%s","%d","%d","%s")' % (t_id, course_id, 2011, 2, class_no))
        tc = d.getOneResult('select * from teacher_course where teacher_id = "%s" and course_id = "%s" and class_no = "%s"' % (t_id, course_id, class_no))
        #print tc['tc_id']
    
    #student_tc
    stc = d.getOneResult('select * from student_tc where student_id = "%s" and tc_id = "%d"' % (s_id, tc['tc_id']))
    if stc:
        continue
    else:
        print s_id
        d.executeSQL('insert into student_tc (student_id, tc_id) values ("%s", "%d")' % (s_id, tc['tc_id']))
