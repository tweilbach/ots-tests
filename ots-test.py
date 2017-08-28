import os
from random import randint
import time
import hashlib
import logging
import datetime
import json
import ntpath
from json import JSONEncoder, JSONDecoder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('ots-test.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)


testFilePath = os.path.join(os.getcwd(), 'testfiles')
datafile = os.path.join(os.getcwd(), 'otsdata.json')

def getRandomInt ():
    return randint(1, 1024)

def writeRandomFile (path):
    filePath = os.path.join(path, str(time.time()) + '.tst')
    with open((filePath), 'wb') as fout:
        fout.write(os.urandom(getRandomInt()))
    return filePath

def getEpochTime ():
    time.time()

def getLocalTimeFromEpoch (epoch):
    return time.strftime('%Y-%m-%d %H:%M:%S:%f', epoch)

def stamp (file):
    try:
        res = os.system(('ots stamp ' + file))
        print(res)
        return True
    except:
        return False

def info (file):
    res = ''
    try:
        res = os.system(('ots -v info ' + file))
        print(res)
        return res
    except:
        return res

def getProofPath (file):
    return file + '.ots'

def loadjson (file):
    with open(file) as json_data:
        return json.loads(json_data.read())

def savejson (file, dataobject):
    with open(file, 'w') as outfile:
        json.dump(json.dumps(Encoder().encode(dataobject)), outfile)


# add json encoder
class Encoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

class ProofStatus:

    def __init__(self, proofcreated, info, upgraded, commited, verified):
        self.proofcreated = proofcreated
        self.commited = commited
        self.info = info
        self.upgraded = upgraded
        self.verified = verified

class Event:

    def __init__(self, name, time, proof, command, message):
        self.name = name
        self.time = time
        self.proof = proof
        self.command = command
        self.message = message

class OtsFile:

    def __init__(self, name, path, proof, proofstatus, size, events):
        self.name = name
        self.path = path
        self.proof = proof
        self.proofstatus = proofstatus
        self.size = size
        self.events = events

# first things first - we load the data
otsdata = []

if os.path.isfile(datafile):
    # load json data
    print(datafile)
    otsdata.append(loadjson(datafile))
    print(otsdata)

#otsdata.append(otsfile)

print(json.dumps(Encoder().encode(otsdata)))

# Create a new file
otsevents = []

filePath = writeRandomFile(testFilePath)
otsevents.append(
    Event(
        'CreateFile',
        getEpochTime(),
        getProofPath(filePath),
        'create',
        'Created new file '+ filePath,
    )
)

committed = stamp(filePath)
otsevents.append(
    Event(
        'StampFile',
        getEpochTime(),
        getProofPath(filePath),
        'stamp',
        ('Stamped file %s with result %s', filePath, committed),
    )
)

#proofpath = getProofPath(filePath)

#print(proofpath)

logger.info('Stamp created for %s', filePath)

 #formulate otsfile object
otsfile = OtsFile(
    os.path.basename(filePath),
    filePath,
    getProofPath(filePath),
    ProofStatus(
        False,
        committed,
        info(getProofPath(filePath)),
        False,
        False
    ),
    os.path.getsize(filePath),
    otsevents
)

# Add it to the object
otsdata.append(otsfile)

# See who should be upgraded and upgrade them

# See who has been upgraded and verify them

# save the object since we're done with it
savejson(datafile, otsdata)

