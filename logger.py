import os
import time

class Logger:
    def __init__(self, dir='.', filepath='log.txt'):        
        if not os.path.isdir(dir):
            os.makedirs(dir)
        fullpath = os.path.join(dir, filepath)
        self.file = open(fullpath, 'a')
        self.file.write('\n'+ time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+'\n')
        self.file.flush()
        

    def __del__(self):
        self.file.close()
        
    def write(self, msg):
        self.file.write(str(msg)+'\n')
        self.file.flush()
        print msg
        
if __name__=='__main__':
    logger = Logger('.', 'debug.txt')
    e = Exception('laksdjkfa')
    logger.write(e)
