# -*- coding: utf-8 -*-
import os
import re
import json
import scrapy
from tqdm import tqdm

# BASE_PATH = "/tmp/"
BASE_PATH = "/Users/daniel/devel/YellowOSM/yellowosm/data-processing/data/raw/"
CRAWLER_DEPOSITS = BASE_PATH + "crawler_deposits/"

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
TARGETSJSON = BASE_PATH + "osm_crawler_at_with_phone_and_website.jsona"  # every line is a valid json string


class YellowosmSpider(scrapy.Spider):
    name = 'yellowosm'

    custom_settings = {
        'LOG_LEVEL': 'CRITICAL'
    }

    def __init__(self):
        super().__init__()
        self.logger.debug(IGNORED_FILES)

    def start_requests(self):
        """return iterable of requests (scrapy.Request(url,...))
        called only once
        default generates list from start_urls"""
        targets = []
        with open(TARGETSJSON, 'r') as myfile:
            for line in myfile.readlines():
                targets.append(json.loads(line))

        for target in tqdm(targets):
            self.logger.debug(target)
            target = target['labels']
            self.logger.info("will scrape: " + target['website'])

            if 'website' in target:
                website = target['website']
            else:
                self.logger.debug("no website found for OSM_ID: " + str(target['osm_id']))
                continue

            if '\\' in website:
                website = website.replace('\\', '/')

            website = website if website.startswith("http") else "http://" + website
            file_name = self.get_url_file_name(website)
            if os.path.isfile(CRAWLER_DEPOSITS + file_name):
                self.logger.debug("website already crawled!")
                continue
            yield (scrapy.Request(url=website, callback=self.parse))

    def get_url_file_name(self, website):
        return re.sub(r"[.?/:*]", "-", website)

    def parse(self, response):
        file_name = self.get_url_file_name(response.url)
        with open(CRAWLER_DEPOSITS + file_name, 'w') as outfile:
            outfile.write(response.text)

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
