import os
import phonenumbers
from tqdm import tqdm


def get_potential_phone_numbers(strings):
    p = []
    for string in strings:
        try:
            number = phonenumbers.parse(string, 'AT')
            if phonenumbers.is_possible_number(number):
                p.append(phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164))
        except phonenumbers.phonenumberutil.NumberParseException:
            pass
    return p


websites = os.listdir('../../data/interim')

for website in tqdm(websites):
    if website == '.gitkeep':
        continue

    with open('../../data/interim/' + website) as infile:
        strings = infile.read().splitlines()

    potential_phone_numbers = get_potential_phone_numbers(strings)

    if not potential_phone_numbers:
        continue

    with open('../../data/processed/potential-phone-numbers/' + website, 'w') as outfile:
        outfile.write('\n'.join(potential_phone_numbers))
