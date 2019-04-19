from bs4 import BeautifulSoup
import os
from tqdm import tqdm

websites = os.listdir('../../data/raw/crawler_deposits')

for website in tqdm(websites):
    if website == '.gitkeep':
        continue

    with open('../../data/raw/crawler_deposits/' + website) as infile:
        soup = BeautifulSoup(infile)

    for script in soup(["script", "style"]):
        script.decompose()
    lines = [line for line in soup.stripped_strings]
    with open('../../data/interim/' + website, 'w') as outfile:
        outfile.write('\n'.join(lines))
