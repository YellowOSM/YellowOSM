import os
from tqdm import tqdm


def is_potential_phone_number(string):
    numbers = sum(c.isdigit() for c in string)
    return numbers > 5


websites = os.listdir('data/interim')

for website in tqdm(websites):
    if website == '.gitkeep':
        continue

    with open('data/interim/' + website) as infile:
        strings = infile.readlines()

    strings = filter(is_potential_phone_number, strings)
    with open('data/processed/potential-phone-numbers' + website, 'w') as outfile:
        outfile.write('\n'.join(strings))
