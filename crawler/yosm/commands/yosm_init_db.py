from scrapy.commands import ScrapyCommand
from sqlalchemy import create_engine
from ..database import Base

class YosmPreprocessCommand(ScrapyCommand):
    def short_desc(self):
        return "YellowOSM: reset and init DB for crawler"

    def run(self, args, opts):
        engine = create_engine('mysql+mysqldb://yellowosm:yellowosm@localhost:5432/yellowosm')
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)