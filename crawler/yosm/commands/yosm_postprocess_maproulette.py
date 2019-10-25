import re
import json
from urllib.parse import urlparse
from tqdm import tqdm
from scrapy.commands import ScrapyCommand
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..database import Base, Website, Poi
from ..helper import Helper

OUTPUT_FILE = 'data/output/maproulette-challenge.json'


class YosmPostprocessMaprouletteCommand(ScrapyCommand):
    def __init__(self):
        super(YosmPostprocessMaprouletteCommand, self).__init__()
        self.helper = Helper()
        engine = create_engine('mysql+mysqldb://yellowosm:yellowosm@localhost:5432/yellowosm')
        Base.metadata.bind = engine
        self.session = sessionmaker(bind=engine)()

    def short_desc(self):
        return "YellowOSM: postprocess found e-mail addresses into a MapRoulette challenge"

    def run(self, args, opts):
        pois = self.session.query(Poi).filter(Poi.email.isnot(None))[:5]
        with open(OUTPUT_FILE, 'w') as outfile:
            for poi in tqdm(pois):
                properties = {
                    'name': poi.name,
                    'address': poi.address,
                    'OSM-ID': poi.osm_id,
                    'website': poi.website.url,
                    'potential email': poi.email,
                }

                outfile.write('{"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": ' +
                              '{"type": "Point", "coordinates": [' + poi.coordinates + ']}, ' +
                              '"properties": ' + json.dumps(properties, ensure_ascii=False)
                              + '}]}\n')
