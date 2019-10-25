import re
import json
from urllib.parse import urlparse
from tqdm import tqdm
from scrapy.commands import ScrapyCommand
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..database import Base, Website, Poi
from ..helper import Helper

INPUT_FILE = 'data/output/osm_pois_without_email_and_with_website.jsona'


class YosmPostprocessCommand(ScrapyCommand):
    def __init__(self):
        super(YosmPostprocessCommand, self).__init__()
        self.helper = Helper()
        self.db_websites = self.helper.get_db_websites()
        self.db_poi_osm_ids = self.helper.get_db_pois()

        engine = create_engine('mysql+mysqldb://yellowosm:yellowosm@localhost:5432/yellowosm')
        Base.metadata.bind = engine
        self.session = sessionmaker(bind=engine)()

    def short_desc(self):
        return "YellowOSM: postprocess crawled websites to extract e-mail addresses"

    def run(self, args, opts):
        targets = []
        with open(INPUT_FILE) as infile:
            for line in infile.readlines():
                targets.append(json.loads(line))

        targets = targets[:100]
        print(len(targets))

        for target in tqdm(targets):
            osm_id = target['labels']['osm_id']

            if osm_id in self.db_poi_osm_ids:
                continue

            ws = None
            email = None
            name = target['labels']['name'] if 'name' in target['labels'] else None
            address = target['labels']['address'] if 'address' in target['labels'] else None
            coordinates = str(target['location'][0]) + ', ' + str(target['location'][1])

            if 'website' in target['labels']:
                website = target['labels']['website']
                website = self.helper.get_standardized_url(website)
                ws = self.session.query(Website).get(website)
                if ws is not None:
                    emails = self.extract_emails(ws.url, ws.html)
                    if len(emails) == 1:
                        email = emails[0]

            poi = Poi(
                osm_id=osm_id,
                website=ws,
                email=email,
                name=name,
                address=address,
                coordinates=coordinates
            )

            self.session.add(poi)

        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise
        finally:
            self.session.close()

    def extract_emails(self, url, html):
        domain = self.get_domain(url)
        # via https://emailregex.com/
        emails = re.findall(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', html)
        emails = [e for e in emails if domain in e]
        return emails

    def get_domain(self, url):
        domain = urlparse(url).netloc
        if domain[:4] == 'www.':
            domain = domain[4:]
        return domain
