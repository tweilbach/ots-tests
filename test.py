import xml.etree.ElementTree
import os
import csv

def vulnversion(version):
    major,minor,build,rev = version.split(".")

    major = int(major)
    minor = int(minor)
    build = int(build)
    rev = int(rev)

    result = True

    if major >= 6 and major <= 11:
        if major == 11 and minor > 6:
            result = False
        elif rev > 3000 :
                result = False
    else:
        result = False

    return result

def writelist(name, line):
    myfile = open(name, 'ab')
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(line)

# path = raw_input('Destination folder:')
basepath = raw_input('Source files directory:')
outfile = raw_input('Output file:')

fileList = []

for filename in os.listdir(basepath):
    if not filename.endswith('.xml'): continue
    fileList.append(os.path.join(basepath, filename))

hostsList = []

for filename in fileList:

    propertiesDict = {}

    #print filename

    root = xml.etree.ElementTree.parse(filename).getroot()

    # for atype in e.findall('SystemDiscovery'):
    for general in root.findall('GeneralInfo'):
        for scs in general.findall('SCSVersion'):
            #print scs.text
            propertiesDict[scs.tag] = scs.text

    for managability in root.findall('ManageabilityInfo'):
        for fwversion in managability.findall('FWVersion'):
            #print fwversion.text
            propertiesDict[fwversion.tag] = fwversion.text
            #propertiesList.append(vulnversion(fwversion.text))
        for capabilities in managability.findall('Capabilities'):
            for atmssupported in capabilities.findall('IsAMTSupported'):
                propertiesDict[atmssupported.tag] = atmssupported.text

        for amtsku in managability.findall('AMTSKU'):
            #print amtsku.text
            propertiesDict[amtsku.tag] = amtsku.text

    for os in root.findall('OSInfo'):
       for host in os.findall('OSHostName'):
            #print host.text
            propertiesDict[host.tag] = host.text

    if 'AMTSKU' in propertiesDict :
        propertiesDict['Vulnerable'] = vulnversion(propertiesDict['FWVersion'])
    else:
        propertiesDict['Vulnerable'] = False
        propertiesDict['AMTSKU'] = 'N/A'

    hostsList.append(propertiesDict)

writelist(outfile, list(hostsList[0].keys()))

for host in hostsList:
    print ", ".join([str(val[1]) for val in host.items()])
    writelist(outfile, list([str(val[1]) for val in host.items()]))