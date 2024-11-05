from abc import ABC, abstractmethod
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import declarative_base, Session

# initiate ORM base
Base = declarative_base()

class Actor(Base):
    __tablename__ = 'actors'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    body_count = Column(Integer)

    def __init__(self, name, fullname, body_count):
        self.name = name
        self.fullname = fullname
        self.body_count = body_count

mysql_username = 'root'
mysql_password = ''
mysql_host = '127.0.0.1:3306'
mysql_database = 'crawl_data'

engine = create_engine(f'mysql+pymysql://{mysql_username}:{mysql_password}@{mysql_host}/{mysql_database}')
metadata = MetaData()
metadata.create_all(engine)
# Kiểm tra kết nối
actors = Table('actors', metadata, autoload_with=engine)

with Session(engine) as session:

    new_actor_1 = Actor(name = "DAC1", fullname="DAC1 DATA", body_count=2)
    new_actor_2 = Actor(name = "DAC2", fullname="DAC2 DATA", body_count=2)
    session.add(new_actor_1)
    session.add(new_actor_2)
    session.commit()

    actors = session.query(Actor).all()
    for actor in actors:
        print(actor.id, actor.name, actor.fullname)