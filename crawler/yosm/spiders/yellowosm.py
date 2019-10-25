import json
import scrapy
from tqdm import tqdm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..items import WebsiteItem
from ..database import Base
from ..helper import Helper

INPUT_FILE = 'data/output/osm_pois_without_email_and_with_website.jsona'  # every line is a valid json string


class YellowosmSpider(scrapy.Spider):
    name = 'yellowosm'

    custom_settings = {
        'LOG_LEVEL': 'ERROR'  # possible values: CRITICAL, ERROR, WARNING, INFO, DEBUG
    }

    def __init__(self):
        super().__init__()
        self.helper = Helper()
        engine = create_engine('mysql+mysqldb://yellowosm:yellowosm@localhost:5432/yellowosm')
        Base.metadata.bind = engine
        self.session = sessionmaker(bind=engine)()
        self.db_websites = self.helper.get_db_websites()

    def start_requests(self):
        """
        return iterable of requests (scrapy.Request(url,...))
        called only once
        default generates list from start_urls
        """
        targets = []
        with open(INPUT_FILE) as infile:
            for line in infile.readlines():
                targets.append(json.loads(line))

        targets = targets[15000:16000]

        print(len(targets))

        for target in tqdm(targets):
            self.logger.debug(target)
            target = target['labels']
            self.logger.info("will scrape: " + target['website'])

            if 'website' in target:
                website = target['website']
            else:
                self.logger.debug("no website found for OSM_ID: " + str(target['osm_id']))
                continue

            website = self.helper.get_standardized_url(website)

            if website in self.db_websites:
                continue

            metadata = {
                'url': website
            }

            yield (scrapy.Request(url=website, callback=self.parse, meta=metadata))

    def parse(self, response):
        url = response.meta.get('url')
        self.db_websites.add(url)
        ws = WebsiteItem(url=url, html=response.text)
        return ws
