import MySQLdb

conn = MySQLdb.connect('localhost', 'root', 'root', 'bioverify_new')
cur = conn.cursor()

#person_info
cur.execute('delete from person_info')
cur.execute('insert into person_info (uuid,name,sex,student_id,grade,department_no) select uuid(),name,sex,student_id,grade,department_no from bioverify.student_info')
cur.execute('commit')

#card_info
cur.execute('delete from card_info')
cur.execute('insert into card_info (card_no,student_id) select card_no,student_id from bioverify.card_info')
cur.execute('update card_info set person_id = (select person_id from person_info where person_info.student_id=card_info.student_id)')
cur.execute('update card_info set person_uuid = (select uuid from person_info where person_info.student_id=card_info.student_id)')
cur.execute('delete from card_info where card_no like "%.0"')
cur.execute('delete from card_info where person_id is null')
cur.execute('commit')

#class
cur.execute('delete from class')
cur.execute('insert into class (uuid,person_id,person_uuid,database_id,create_time,type,subtype) select bioverify.class.uuid,person_id,person_info.uuid,1016,bioverify.class.create_time,1,type from bioverify.class left join person_info on bioverify.class.student_id=person_info.student_id')
cur.execute('delete from class where person_id is null')
cur.execute('commit')

#sample
cur.execute('delete from sample')
cur.execute('insert into sample (uuid,person_id,person_uuid,database_id,create_time,file,class_uuid,class_id) \
            select bioverify.sample.uuid,person_info.person_id,person_info.uuid,\
            1016,bioverify.sample.create_time,bioverify.sample.file,bioverify.sample.class_uuid,class.class_id from \
            bioverify.sample left join person_info on bioverify.sample.student_id = person_info.student_id \
            left join class on class.uuid=bioverify.sample.class_uuid \
')
cur.execute('delete from sample where class_id is null')
cur.execute('commit')

#template
cur.execute('delete from template')
cur.execute('insert into template (uuid,person_id,person_uuid,database_id,modify_time,file,class_uuid,class_id,sample_uuid,sample_id, valid) \
            select bioverify.template.uuid,person_info.person_id,person_info.uuid,\
            1016,bioverify.template.create_time,bioverify.template.file,bioverify.template.class_uuid,class.class_id, \
            bioverify.template.sample_uuid,sample.sample_id,bioverify.template.valid from\
            bioverify.template left join person_info on bioverify.template.student_id = person_info.student_id \
            left join class on class.uuid=bioverify.template.class_uuid \
            left join sample on sample.uuid=bioverify.template.sample_uuid \
')
cur.execute('delete from template where sample_id is null')
cur.execute('update template set algorithm_id = 1')
cur.execute('commit')