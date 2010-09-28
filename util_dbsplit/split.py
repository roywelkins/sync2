import MySQLdb
import sys
import os

prog = sys.argv[0]
usage_msg = "USAGE: %s [mysqlhost] [mysqluser] [mysqlpasswd] [mysqlschema] [fromroot] [toroot]" % prog

if len(sys.argv)!=7:
    print usage_msg
    exit(0)
    
(prog, host, user, passwd, schema, fromroot, toroot) = sys.argv
conn = MySQLdb.connect(host, user, passwd, schema)
cursor = conn.cursor()
cursor.execute('select file from sample')
spfiles = cursor.fetchall()
spfiles = [c[0] for c in spfiles]

cursor.execute('select file from template')
tpfiles = cursor.fetchall()
tpfiles = [c[0] for c in tpfiles]

files = spfiles+tpfiles
i = 0
t = len(files)
for f in files:
    frompath = os.path.join(fromroot, f)
    topath = os.path.join(toroot, f)
    if os.path.isfile(topath):
        continue
    todir = os.path.dirname(topath)    
    if not os.path.isdir(todir):
        os.makedirs(todir)
    os.system('copy %s %s >> stdout.txt' % (frompath, topath))
    i = i+1
    print '\r%d/%d' % (i, t),