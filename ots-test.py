#!/usr/bin/env python3

import os
from random import randint
import logging
from pymongo import MongoClient
import subprocess
import time
from time import mktime
from datetime import datetime

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

# setup connection to mongo instance
client = MongoClient("localhost")
db = client.ots


testFilePath = os.path.join(os.getcwd(), 'testfiles')

def insertOtsObj(file):
    res = db.otsfiles.insert_one(file)
    print(res)


def getRandomInt ():
    return randint(1, 1024)


def writeRandomFile (path):
    filePath = os.path.join(path, str(time.time()) + '.tst')
    with open((filePath), 'wb') as fout:
        fout.write(os.urandom(getRandomInt()))
    return filePath


def getProofTimestamp(proofstring):
    # split the string and get the time component
    tstime = proofstring.split("as of ", 1)[1]
    # format the time string
    time_tuple = time.strptime(tstime, '%a %b %d %H:%M:%S %Y %Z')
    # Make a datetime object from fortmatted time
    dt = datetime.fromtimestamp(mktime(time_tuple))
    #return timestamp
    return dt.timestamp()


def getLocalTimeFromEpoch (epoch):
    return time.strftime('%Y-%m-%d %H:%M:%S:%f', epoch)

def stamp (file):
    try:
        res = subprocess.getoutput('~/Downloads/Code/opentimestamps-client/ots stamp ' + file)
        print(res)
        return True
    except:
        return False

def info (file):
    res = ''
    try:
        res = subprocess.getoutput('~/Downloads/Code/opentimestamps-client/ots -v info ' + file)
        print(res)
        return res
    except:
        return res

def upgrade (file):
    res = subprocess.getoutput('~/Downloads/Code/opentimestamps-client/ots upgrade ' + file)
    print (res)
    if res.__contains__("Success! Timestamp complete"):
        return True
    else:
        return False

def verify(file):
    res = subprocess.getoutput('~/Downloads/Code/opentimestamps-client/ots verify ' + file)
    print(res)
    return res

def getProofPath (file):
    return file + '.ots'

def parseVerifiedDate(date):
    parts = date.split()

#print(json.dumps(Encoder().encode(otsdata)))
def create_new_file():

    otsevent = {
        'name': '',
        'time': '',
        'command': '',
        'message': ''
    }
    otsproof = {
        'created': False,
        'committed': False,
        'info': '',
        'upgraded': False,
        'verified': False
    }
    otsobj = {
        'name': '',
        'path': '',
        'proof': '',
        'events': [],
        'size': ''
    }
    filePath = writeRandomFile(testFilePath)
    otsobj['events'].append({
        'name': 'CreateFile',
        'time': time.time(),
        'command': 'create',
        'message': 'Created new file ' + filePath
    })

    #stamp that thaang
    committed = stamp(filePath)
    #committed = False

    #update otsproof
    otsproof['created'] = True
    otsproof['createdTime'] = time.time()
    otsproof['committed'] = committed
    otsproof['info'] = info(getProofPath(filePath))

    otsobj['events'].append({
        'name': 'StampFile',
        'time': time.time(),
        'command': 'stamp',
        'message': 'Stamped file '+filePath+' with result '+ str(committed)
    })
    # proofpath = getProofPath(filePath)
    # print(proofpath)
    logger.info("Stamp created for %s", filePath)
    otsobj['name'] = os.path.basename(filePath)
    otsobj['path'] = filePath
    otsobj['proof'] = otsproof
    otsobj['size'] = os.path.getsize(filePath)
    # formulate otsfile object
    # Add it to the db
    insertOtsObj(otsobj)

def verify_timestamp():
    otsobjs = db.otsfiles.find({"proof.upgraded": True, "proof.verified": False})

    # loop through all the non-upgraded stamps and upgrade them
    for otsobj in otsobjs:
        # print(str(otsobj))
        # get the object id so we can reference it later
        _id = otsobj['_id']
        #print(_id)
        #print(otsobj)
        #print(getProofPath(otsobj['path']))
        logger.info("Found obj ready to verify at %s with ID %s" % (getProofPath(otsobj['path']), _id))

        res = verify(getProofPath(otsobj['path']))
        logger.info("Found obj with ID %s. Verification result %s" % (_id, res))

        if res.__contains__('Pending confirmation in Bitcoin blockchain'):
            verified = False
        elif res.__contains__('Success! Bitcoin attests data existed'):
            verified = True

        otsevent = {
            'name': 'VerifyFile',
            'time': time.time(),
            'command': 'verify',
            'message': 'Performed a verification and the result was ' + str(res)
        }

        # update the proof
        otsobj['proof']['verified'] = True
        otsobj['proof']['verifiedTime'] = getProofTimestamp(res)
        otsobj['proof']['info'] = res
        otsobj['proof']['attestationDetail'] = info(getProofPath(otsobj['path']))
        # add the event
        otsobj['events'].append(otsevent)

        # update obj based on _id
        db.otsfiles.replace_one({"_id": _id}, otsobj)

def upgrade_timestamps():
    otsobjs = db.otsfiles.find({"proof.upgraded": False})

    # loop through all the non-upgraded stamps and upgrade them
    for otsobj in otsobjs:
        #print(str(otsobj))
        # get the object id so we can reference it later
        _id = otsobj['_id']

        logger.info("Found obj ready to upgrade at %s with ID %s" % (getProofPath(otsobj['path']), _id))
        #print(_id)
        # perfrom teh upgrade
        res = upgrade(getProofPath(otsobj['path']))

        logger.info("Found obj with ID %s. Upgrade result %s" % (_id, res))

        #print(str(res))
        # create an event for the upgrade
        otsevent = {
            'name': 'UpgradeFile',
            'time': time.time(),
            'command': 'upgrade',
            'message': 'Performed an upgrade and the result was ' + str(res)
        }

        # update the proof
        otsobj['proof']['upgraded'] = res
        # add the event
        otsobj['events'].append(otsevent)

        #update obj based on _id
        db.otsfiles.replace_one({"_id": _id}, otsobj)



_starttime = time.time()
# Create and save new file
logger.info("Create new file started")
create_new_file()
logger.info("Create new file ended")

# See who should be upgraded and upgrade them
logger.info("Upgrade timestamps started")
upgrade_timestamps()
logger.info("Upgrade timestamps ended")

# See who has been upgraded and verify them
logger.info("Verify timestamps started")
verify_timestamp()
logger.info("Verify timestamps ended")
_endtime = time.time()

logger.info("Process started at %s and ended at %s. Complete run time: %s seconds" % (_starttime, _endtime, str(_endtime - _starttime)))