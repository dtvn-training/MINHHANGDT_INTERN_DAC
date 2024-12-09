from sqlalchemy import Column, String, Float, Text
from .app import AppData

class AndroidApp(AppData):
    __tablename__ = 'app_android'

    app_id = Column(String(250), primary_key=True)
    app_name = Column(String(200))
    category = Column(String(100))
    price = Column(String(100))
    provider = Column(String(100))
    description = Column(Text)
    developer_email = Column(String(100))

    def __init__(self, app_id, app_name, category, price, provider, description, developer_email):
        super().__init__(app_id, app_name, category, provider, description)
        self.price = price
        self.developer_email = developer_email
