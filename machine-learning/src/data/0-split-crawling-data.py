import json

with open('../../data/raw/osm_es_export_20190419.json') as infile:
    targets = [line.strip() for line in infile.read().splitlines() if not line.startswith('{"index": ')]

irrelevant_targets = []
relevant_targets = []
for t in targets:
    data = json.loads(t)
    if 'website' in data['labels']:
        if 'wegweiser' in data['labels']['website'] or 'phone' in data['labels']:
            irrelevant_targets.append([])
        else:
            relevant_targets.append(t)

print('%d lines in database, of which %d with both phone and website and %d without phone but with website' %
      (len(targets), len(irrelevant_targets), len(relevant_targets)))

with open('../../data/raw/osm_crawler_at_without_phone_and_with_website.jsona', 'w') as outfile:
    outfile.write('\n'.join(relevant_targets))
