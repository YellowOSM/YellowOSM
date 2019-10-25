# -*- coding: utf-8 -*-
from .database import Base, Website, Poi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Helper(object):
    def __init__(self):
        engine = create_engine('mysql+mysqldb://yellowosm:yellowosm@localhost:5432/yellowosm')
        Base.metadata.bind = engine
        self.session = sessionmaker(bind=engine)()

    def get_db_websites(self):
        websites = self.session.query(Website).all()
        return set(w.url for w in websites)

    def get_standardized_url(self, url):
        url = url.replace('\\', '/')
        url = url if url.startswith("http") else "http://" + url
        return url

    def get_db_pois(self):
        pois = self.session.query(Poi).all()
        return set(w.osm_id for w in pois)
