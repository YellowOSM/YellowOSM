# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .database import Base, Website


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class MySQLPipeline(object):
    def __init__(self):
        engine = create_engine('mysql+mysqldb://yellowosm:yellowosm@localhost:5432/yellowosm')
        Base.metadata.bind = engine
        self.session = sessionmaker(bind=engine)()

    def process_item(self, item, spider):
        ws = Website(**item)
        self.session.add(ws)
        return ws

    def close_spider(self, spider):
        # We commit and save all items to DB when spider finished scraping.
        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise
        finally:
            self.session.close()
