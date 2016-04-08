from easysnmp import Session, snmp_get, snmp_set, snmp_walk
import json
import pprint 
import re
import sys

HOST=sys.argv[1]
VER=2
COMMUNITY=sys.argv[2]
TIMEOUT=2

if_matches = ['^eth0', 'docker0']
if_oids = {
    "ifName": ".1.3.6.1.2.1.31.1.1.1.1",  # IF OS Name
#    "ifIP": ".1.3.6.1.2.1.4.20.1.2",  # IF IP Addr
    "BytesIN": ".1.3.6.1.2.1.31.1.1.1.6",  # IN BYTES 64 bit counters
    "BytesOUT": ".1.3.6.1.2.1.31.1.1.1.10",  # OUT BYTES 64 bit counters
    "uPktsIN": ".1.3.6.1.2.1.2.2.1.11",  # IN uCast PKTS counters
    "uPktsOUT": ".1.3.6.1.2.1.2.2.1.17",  # OUT uCast PKTS counters
    "DiscardsIN": ".1.3.6.1.2.1.2.2.1.13",  # IN Discarded PKTS counters
    "DiscardsOUT": ".1.3.6.1.2.1.2.2.1.19",  # OUT Discarded PKTS counters
    "ErrsIN": ".1.3.6.1.2.1.2.2.1.14",  # OUT Error counters
    "ErrsOUT": ".1.3.6.1.2.1.2.2.1.20",  # OUT Error counters
}


disk_matches = ['xvd']
disk_oids = {
    "Dev": ".1.3.6.1.4.1.2021.9.1.3",  # Device & mount point
    "TotalSpace": ".1.3.6.1.4.1.2021.9.1.6",  # Storage size/capacity
    "UsedSpace": ".1.3.6.1.4.1.2021.9.1.8",  # Storage size/capacity
}

# Light up an snmp session
session = Session(hostname=HOST, community=COMMUNITY, version=VER)

def get_dev_indexes(oid, matches):
    # Find matching interfaces and get Indexes
    indexes = []
    # Walk the oid we were passed
    snmpout = walk(oid)
    # Loop through the matches to see if we have any and populate the index list
    for device in matches:
        for item in snmpout:
            if re.search(device, item.value):
                indexes.append({"dev": item.value, "dev_index": item.oid_index})
    return indexes

# Do the walk
def walk(oid_prefix):
    snmpout = session.walk(oid_prefix)
    return snmpout

def get(oid):
    snmpout = session.get(oid)
    return snmpout

def build_json(indexes, oids):
    dataout = list()
    for ind in indexes:
        data = {
            'name': ind['dev'],
            'oids': []
        }

        for item in oids.items():
            data['oids'].append(
                {
                    "name": item[0],
                    "oid": ".".join([item[1], ind['dev_index']])
                }
            )
        dataout.append(data)
    return dataout

if_indexes = get_dev_indexes(if_oids["ifName"], if_matches)
disk_indexes = get_dev_indexes(disk_oids["Dev"], disk_matches)


print json.dumps(build_json(if_indexes, if_oids), indent=4)
print json.dumps(build_json(disk_indexes, disk_oids), indent=4)
