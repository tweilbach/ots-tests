import os
from random import randint
import time
import hashlib


testFilePath = os.path.join(os.getcwd(), 'testfiles')

def getRandomInt ():
    return(randint(1, 1024))

def writeRandomFile (path):
    with open(os.path.join(path, str(time.time()) + '.tst'), 'wb') as fout:
        fout.write(os.urandom(getRandomInt()))

def getEpochTime ():
    time.time()

def getLocalTimeFromEpoch (epoch):
    return time.strftime('%Y-%m-%d %H:%M:%S:%f', epoch)


writeRandomFile(testFilePath)