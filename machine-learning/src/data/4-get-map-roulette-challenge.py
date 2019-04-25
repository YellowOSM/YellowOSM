import json
import re


def get_website_file_name(website):
    if '\\' in website:
        website = website.replace('\\', '/')
    website = website if website.startswith("http") else "http://" + website
    return re.sub(r"[.?/:*]", "-", website)


targets = []
with open('../../data/raw/osm_crawler_at_without_phone_and_with_website.jsona') as infile:
    for line in infile.read().splitlines():
        targets.append(json.loads(line))

relevant_targets = []
for t in targets:
    l = t['labels']
    if l['osm_id'] and 'website' in l and 'phone' not in l:
        relevant_targets.append(t)

with open('../../data/export/map-roulette-challenge.json', 'w') as outfile:
    # idx <= 10 was used in first challenge
    # 10 < idx <= 1510 was used in second challenge
    idx = 10
    for t in relevant_targets:
        if idx >= 1510:
            break
        website_file_name = get_website_file_name(t['labels']['website'])
        try:
            with open('../../data/processed/potential-phone-numbers/' + website_file_name) as infile:
                strings = set(infile.read().splitlines())
        except:
            continue

        if not strings:
            continue

        properties = {
            'name': t['name'],
            'type': t['type'],
            'OSM-ID': str(t['labels']['osm_id']),
            'website': t['labels']['website'],
        }
        if 'address' in t['labels']:
            properties['address'] = t['labels']['address']

        for i, potential_phone in enumerate(strings):
            properties['potential phone number ' + str(i + 1)] = potential_phone

        outfile.write('{"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": ' +
                      '{"type": "Point", "coordinates": [' + str(t['location'][0]) +
                      ', ' + str(t['location'][1]) + ']}, ' +
                      # '"properties": ' + ','.join('"' + k + '": "' + v.replace('"', '\\"') + '"' for k, v in properties.items()) + '}'
                       '"properties": ' + json.dumps(properties, ensure_ascii=False)
                      + '}]}\n')
        idx += 1
