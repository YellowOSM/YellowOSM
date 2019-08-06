from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Website(Base):
    __tablename__ = 'website'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    url = Column(String(500), nullable=False, primary_key=True)
    html = Column(Text(16000000), nullable=False)
    emails = relationship('Email')


class Poi(Base):
    __tablename__ = 'poi'
    osm_id = Column(String(50), nullable=False, primary_key=True)
    name = Column(String(500), nullable=True)
    website_url = Column(String(500), ForeignKey('website.url'))
    website = relationship(Website)
    email = Column(String(200), nullable=True)
    phone = Column(String(100), nullable=True)


class Email(Base):
    __tablename__ = 'email'
    id = Column(Integer, primary_key=True)
    website_url = Column(String(500), ForeignKey('website.url'))


# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.

# engine = create_engine('mysql+mysqldb://yellowosm:yellowosm@localhost:5432/yellowosm')
# connection = engine.connect()
# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)
