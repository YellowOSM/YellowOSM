from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Website(Base):
    __tablename__ = 'website'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    url = Column(String(500), nullable=False, primary_key=True)
    html = Column(Text(16000000), nullable=False)


class Poi(Base):
    __tablename__ = 'poi'
    osm_id = Column(String(50), nullable=False, primary_key=True)
    name = Column(String(500), nullable=True)
    address = Column(String(500), nullable=True)
    coordinates = Column(String(200), nullable=True)
    website_url = Column(String(500), ForeignKey('website.url'))
    website = relationship(Website)
    email = Column(String(200), nullable=True)
