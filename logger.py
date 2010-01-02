import os
import conf
import time

class Logger:
    def __init__(self, filepath):        
        if not os.path.isdir(conf.logdir):
            os.makedirs(conf.logdir)
        fullpath = os.path.join(conf.logdir, filepath)
        self.file = open(fullpath, 'a')
        self.file.write('\n'+ time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+'\n')

    def __del__(self):
        self.file.close()
