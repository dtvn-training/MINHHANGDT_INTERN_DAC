from sqlalchemy import Column, String, Float, Integer, Text
from ..database import Base

class AppData(Base):
    __abstract__ = True

    def __init__(self, app_id, app_name, category, price, provider, description):
        self.app_id = app_id
        self.app_name = app_name
        self.category = category
        self.price = price
        self.provider = provider
        self.description = description