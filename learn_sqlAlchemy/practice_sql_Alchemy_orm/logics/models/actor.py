from sqlalchemy import Column, Integer, String
from logics.database import Base

class Actor(Base):
    __tablename__ = 'actors'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    fullname = Column(String(250))
    body_count = Column(Integer)

    def __init__(self, name, fullname, body_count):
        self.name = name
        self.fullname = fullname
        self.body_count = body_count
