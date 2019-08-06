# -*- coding: utf-8 -*-
import os
import re
import json
import scrapy
from tqdm import tqdm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from scraperone.spiders.database_tables import Base, Website, Poi
from scrapy import signals

IGNORED_FILES = [
    ".pdf",
    ".jpg",
    ".jpeg",
    ".gif",
    ".png",
    ".tiff",
    ".pdf",
]
IGNORED_FILES.extend([ft.upper() for ft in IGNORED_FILES])
NO_FOLLOW_LINK = [
    "tel:",
    "mailto:",
    "callto:",
]

BASE_PATH = "/Users/daniel/devel/YellowOSM/yellowosm/machine-learning/data/raw/"
CRAWLER_DEPOSITS = BASE_PATH + "crawler_deposits/"
TARGETSJSON_WITHOUT_EMAIL = BASE_PATH + "osm_crawler_at_without_email_and_with_website.jsona"  # every line is a valid json string


class YellowosmSpider(scrapy.Spider):
    name = 'yellowosm'

    custom_settings = {
        'LOG_LEVEL': 'CRITICAL'
    }

    def __init__(self):
        super().__init__()
        self.logger.debug(IGNORED_FILES)
        engine = create_engine('mysql+mysqldb://yellowosm:yellowosm@localhost:5432/yellowosm')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
        self.uncomitted = 0
        self.db_websites = self.get_db_websites()
        self.db_poi_osm_ids = self.get_db_osm_ids()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(YellowosmSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def get_db_websites(self):
        websites = self.session.query(Website).all()
        return set(w.url for w in websites)

    def get_db_osm_ids(self):
        pois = self.session.query(Poi).all()
        return set(p.osm_id for p in pois)

    def start_requests(self):
        """
        return iterable of requests (scrapy.Request(url,...))
        called only once
        default generates list from start_urls
        """
        targets = []
        for jsona_file_name in [
            TARGETSJSON_WITHOUT_EMAIL
        ]:
            with open(jsona_file_name) as infile:
                for line in infile.readlines():
                    targets.append(json.loads(line))

        print('restricting targets to 100')
        targets = targets[:100]

        print(len(targets))

        for target in tqdm(targets):
            self.logger.debug(target)
            target = target['labels']
            if target['osm_id'] in self.db_poi_osm_ids:
                self.logger.debug('OSM ID already in database - skipping')
                continue
            self.logger.info("will scrape: " + target['website'])

            if 'website' in target:
                website = target['website']
            else:
                self.logger.debug("no website found for OSM_ID: " + str(target['osm_id']))
                continue

            if '\\' in website:
                website = website.replace('\\', '/')

            website = website if website.startswith("http") else "http://" + website
            metadata = {
                'name': target['name'] if 'name' in target else None,
                'osm_id': target['osm_id'],
                'email': target['email'] if 'email' in target else None,
                'phone': target['phone'] if 'phone' in target else None,
            }
            if website in self.db_websites:
                self.logger.debug("website already crawled!")
                ws = self.session.query(Website).get(website)
                poi = Poi(
                    osm_id=metadata['osm_id'],
                    name=metadata['name'],
                    phone=metadata['phone'],
                    website=ws
                )
                self.db_poi_osm_ids.add(poi.osm_id)
                self.session.add(poi)
                self.session.commit()
                self.uncomitted = 0
                continue

            yield (scrapy.Request(url=website, callback=self.parse, meta=metadata))

    def parse(self, response):
        original_url = response.url
        if 'redirect_urls' in response.request.meta:
            original_url = response.request.meta['redirect_urls'][-1]
        ws = Website(url=original_url, html=response.text)
        self.db_websites.add(ws.url)
        self.session.add(ws)
        poi = Poi(
            osm_id=response.meta.get('osm_id'),
            name=response.meta.get('name'),
            phone=response.meta.get('phone'),
            website=ws
        )
        self.db_poi_osm_ids.add(poi.osm_id)
        self.session.add(poi)
        self.uncomitted += 1
        if self.uncomitted > 100:
            self.session.commit()
            self.uncomitted = 0

    def spider_closed(self, spider):
        self.session.commit()

    def clean_html(self, text):
        newline_remover = re.compile('\n')
        text = re.sub(newline_remover, '', text)
        splitter = re.compile('<.*?>')
        clean_text_snippets = re.split(splitter, text)
        clean_text_snippets = [snip for snip in clean_text_snippets if snip]
        return clean_text_snippets

    def parse_old(self, response):
        url = ''.join(response.url.split('/')[2])
        path = '_'.join(response.url.split('/')[3:])
        # mkdir with url as dir
        url_path = CRAWLER_DEPOSITS + YellowosmSpider.name + "/" + url
        os.makedirs(url_path, exist_ok=True)

        contact_path = url_path + "/yosm_contact" + "_" + path
        strings_path = url_path + "/yosm_strings" + "_" + path
        hrefs_path = url_path + "/yosm_hrefs" + "_" + path

        dom_path = url_path + '/' + path
        if path == "":
            path = "index"
            dom_path = url_path + '/' + path

        # dump DOMS there
        self.logger.debug("dom_path: " + dom_path)
        with open(dom_path, 'w') as dom_file:
            dom_file.write(response.text)
        tels = []
        mails = []
        for href in response.xpath('//a/@href').getall():
            if href.startswith("mailto:"):
                mails.append(href)
            if href.startswith("tel:"):
                tels.append(href)

        with open(hrefs_path, 'w') as hrefs_file:
            for href in response.xpath('//a/@href').getall():
                hrefs_file.write(href + "\n")

        with open(strings_path, 'w') as strings_file:
            for text in self.clean_html(response.text):
                strings_file.write(text.strip() + "\n")

        self.logger.debug("contact_path: " + contact_path)
        if mails or tels:
            with open(contact_path, 'w') as contact_file:
                for mail in mails:
                    contact_file.write(mail + "\n")
                for tel in tels:
                    contact_file.write(tel + "\n")

        for href in response.xpath('//a/@href').getall():
            for el in IGNORED_FILES:
                if href.endswith(el):
                    continue
            for el in NO_FOLLOW_LINK:
                if href.startswith(el):
                    continue
            yield scrapy.Request(response.urljoin(href), self.parse)
