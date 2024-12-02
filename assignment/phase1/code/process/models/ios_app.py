from sqlalchemy import Column, String, Float, Text, Integer
from .app import AppData

class IosApp(AppData):
    __tablename__ = 'app_ios'

    app_id = Column(String(250), primary_key=True)
    app_name = Column(String(200))
    category = Column(String(100))
    price = Column(Float)
    provider = Column(String(1000))
    description = Column(Text)
    score = Column(Float)
    cnt_rates = Column(Integer)
    subtitle = Column(String(1000))
    link = Column(Text)
    img_links = Column(Text)

    def __init__(self, app_id, app_name, category, price, provider, description, score, cnt_rates, subtitle, link, img_links):
        super().__init__(app_id, app_name, category, price, provider, description)
        self.score = score
        self.cnt_rates = cnt_rates
        self.subtitle = subtitle
        self.link = link
        self.img_links = img_links