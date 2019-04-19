import os
import re
import json
import phonenumbers
from tqdm import tqdm


def get_website_file_name(website):
    if '\\' in website:
        website = website.replace('\\', '/')
    website = website if website.startswith("http") else "http://" + website
    return re.sub(r"[.?/:*]", "-", website)


def normalize_phone_number(string):
    try:
        number = phonenumbers.parse(string, 'AT')
        if phonenumbers.is_possible_number(number):
            return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.phonenumberutil.NumberParseException:
        pass
    return False


targets = []
with open('../../data/raw/osm_crawler_at_with_phone_and_website.jsona') as infile:
    for line in infile.read().splitlines():
        targets.append(json.loads(line))
relevant_targets = []
for t in targets:
    l = t['labels']
    if not l['osm_id'] or not l['website'] or not l['phone']:
        continue
    relevant_targets.append([str(l['osm_id']), l['phone'], l['website'], get_website_file_name(l['website'])])

print('%d OSM entries, of which %d with website and phone number' % (len(targets), len(relevant_targets)))

websites = set(os.listdir('../../data/processed/potential-phone-numbers'))

print('%d potential websites' % (len(websites)))

found_targets = []
for t in tqdm(relevant_targets):
    if t[-1] not in websites:
        continue

    normalized_phone_number = normalize_phone_number(t[1])
    if not normalized_phone_number:
        continue

    with open('../../data/processed/potential-phone-numbers/' + t[-1]) as infile:
        strings = set(infile.read().splitlines())

    if normalized_phone_number in strings:
        found_targets.append(t)

print('%d matches found' % (len(found_targets)))

with open('../../data/processed/results.csv', 'w') as outfile:
    outfile.write('osm_id,osm_phone,osm_website,website_file\n')
    outfile.write('\n'.join([','.join(f) for f in found_targets]))

with open('../../data/raw/osm_es_export_20190419.json') as infile:
    targets = [line.strip() for line in infile.read().splitlines() if not line.startswith('{"index": ')]

irrelevant_targets = []
relevant_targets = []
for t in targets:
    data = json.loads(t)
    if 'website' in data['labels']:
        if 'phone' not in data['labels']:
            relevant_targets.append(t)
        else:
            irrelevant_targets.append([])

print('%d lines in database, of which %d with both phone and website and %d without phone but with website' %
      (len(targets), len(irrelevant_targets), len(relevant_targets)))

with open('../../data/raw/osm_crawler_without_phone_and_with_website.jsona', 'w') as outfile:
    outfile.write('\n'.join(relevant_targets))
