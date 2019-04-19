#!/usr/bin/python3
import sys
import json

# grep website /tmp/osm_es_export.json | sed 's/^\(.*\)"osm_id": "\([^"]*\)".*website": "\([^"]*\)".*$/\2,\3/;' | shuf -n 200

args = sys.argv

if len(args) > 1:
    datafile = args[1]
else:
    raise ValueError("""input file provide you must!\nrun:\n{} <your_input_file.json>""".format(args[0]))


class Element():
    def __init__(self, line):
        self.data = json.loads(line)

    def __repr__(self):
        return str(self.data)


with open(datafile, 'r') as f:
    for line in f.readlines():
        if line.startswith('{"index": '):
            continue
        el = Element(line)
        if 'website' in el.data['labels'] or 'contact_website' in el.data['labels']:
            if 'phone' in el.data['labels']:
                print(json.dumps(el.data))
                # print(el)
        # print(el)
        # print(line,end="")
