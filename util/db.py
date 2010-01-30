import MySQLdb

conn = MySQLdb.connect('localhost', 'root', 'root', 'bioverify_new')
cur = conn.cursor()

#person_info
#cur.execute('delete from person_info')
#cur.execute('insert into person_info (uuid,name,sex,student_id,grade,department_no) select uuid(),name,sex,student_id,grade,department_no from bioverify.student_info')
#cur.execute('commit')

#card_info
#cur.execute('delete from card_info')
#cur.execute('insert into card_info (card_no,student_id) select card_no,student_id from bioverify.card_info')
#cur.execute('update card_info set person_id = (select person_id from person_info where person_info.student_id=card_info.student_id)')
#cur.execute('update card_info set person_uuid = (select uuid from person_info where person_info.student_id=card_info.student_id)')
#cur.execute('delete from card_info where card_no like "%.0"')
#cur.execute('commit')

