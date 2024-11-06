from abc import ABC, abstractmethod
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from google_play_scraper import app, Sort, reviews_all
from bs4 import BeautifulSoup
import requests
import json
import re

# initiate ORM base
Base = declarative_base()

# Abstract class AppData
class AppData(Base):
    __abstract__ = True  # Đánh dấu đây là abstract class

    def __init__(self, app_id, app_name, category, price, provider, description):
        self.app_id = app_id
        self.app_name = app_name
        self.category = category
        self.price = price
        self.provider = provider
        self.description = description

#ORM mapping for AndroidApp
class AndroidApp(AppData):
    __tablename__ = 'app_android'

    #define columns of table
    #app_id, app_name, category, price, provider, description, developer_email

    app_id = Column(String(250), primary_key=True)
    app_name = Column(String(200))
    category = Column(String(100))
    price = Column(Float)
    provider = Column(String(100))
    description = Column(Text)
    developer_email = Column(String(100))

    def __init__(self, app_id, app_name, category, price, provider, description, developer_email):
        super().__init__(app_id, app_name, category, price, provider, description)
        self.developer_email = developer_email

#ORM mapping for IosApp
class IosApp(AppData):
    __tablename__ = 'app_ios'

    app_id = Column(String(5), primary_key=True)
    app_name = Column(String(200))
    category = Column(String(100))
    price = Column(Float)
    provider = Column(String(100))
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

class AndroidDataCollector:
    """Android data collector Class"""

    def __init__(self):
        self.android_apps = []

    def collect_android_data(self, app_ids):
        """
        Crawl app data from Google Play Store base on app_ids
        """
        for app_id in app_ids:
            try:
                # crawl app through app_id
                result = app(
                    app_id,
                    lang = 'en',
                    country = 'vi'
                )

                #create instance of AndroidApp from crawl data
                android_app = AndroidApp(
                    app_id=app_id,
                    app_name=result.get("title", "Unknown"),
                    category=result.get("genre", "Unknown"),
                    price = float(result.get("price", "0")),
                    provider = result.get("developer", "Unknown"),
                    description=result.get("description", "Unknown"),
                    developer_email= result.get("developerEmail", "Unknown"),
                )

                self.android_apps.append(android_app)

            except Exception as e:
                print(f"Failed to crawl app {app_id}: {e}")

    def get_collected_android_apps(self):
        return self.android_apps

class IosDataCollector:
    """Ios data collector Class"""
    def __init__(self):
        self.ios_apps = []

class DataStore:
    """Data Store class"""
    def __init__(self):
        return
    
def list_to_string(data):
    """turn list into list"""
    return

def extract_quoted_strings(data):
    """extract string inside quote sign"""
    return

def find_list_android_app_ids(language, country, length, chart_name, category_id):
    """find list of android_app's id"""
    return

def find_df_ios_app(url):
    """find list of ios_app contain rank, title, subtitle, link, img_links"""
    return

def crawl_android(language, country, chart_name, category_id):
    """crawl android apps"""
    return

def main_android():
    
    return

def crawl_ios(url):
    """crawl ios apps"""
    return

def main_ios():
    return

if __name__ == "__main__":
    main_android()
    main_ios()