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

    def collect_ios_data(self, df_ids):
        """
        Crawl app data from Google Play Store base on app_ids
        """
        for index, row in df_ids.iterrows():
            url = row['link']
            resp = requests.get(url)
            bs_soup = BeautifulSoup(resp.text, 'html.parser')

            secs_list = bs_soup.find_all('section', class_='l-content-width section section--bordered')

            secs_des = secs_list[1]
            description = secs_des.find('p').get_text()
            
            if len(secs_list) >= 3:
                try:
                    secs = secs_list[2]
                    score = secs.find('div', class_='we-customer-ratings lockup').find(
                        'div', class_='we-customer-ratings__stats l-column small-4 medium-6 large-4'
                    ).find('div', class_='we-customer-ratings__averages').find('span').get_text()

                    cnt_rates = Integer(secs.find('div', class_='we-customer-ratings lockup').find(
                        'div', class_='we-customer-ratings__stats l-column small-4 medium-6 large-4'
                    ).find('div', class_='we-customer-ratings__count small-hide medium-show').get_text(strip=True).split()[0])
                    
                except:
                    score = 0
                    cnt_rates = 0
            else:
                score = 0
                cnt_rates = 0

            cater_ls = bs_soup.find_all('section', class_='l-content-width section section--bordered section--information')

            cate = cater_ls[0]
            siz = cate.find('div', class_="information-list__item l-column small-12 medium-6 large-4 small-valign-top").find(
                'dd', class_="information-list__item__definition"
            ).get_text()

            category = cate.find('dl', class_="information-list information-list--app medium-columns l-row").find_all(
                'dd', class_="information-list__item__definition"
            )[2].get_text()

            provider = cate.find('dl', class_="information-list information-list--app medium-columns l-row").find_all(
            'dd', class_="information-list__item__definition"
            )[0].get_text()

            ios_app = IosApp(
                    app_id=row['rank'],
                    app_name=row['title'],
                    category=category,
                    price = 0.0,
                    provider = provider,
                    description=description,
                    score = score,
                    cnt_rates = cnt_rates,
                    subtitle = row['subtitle'],
                    link = row['link'],
                    img_links = ','.join(row['img_links'])
                )
            
            self.ios_apps.append(ios_app)

    def get_collected_ios_apps(self):
        return self.ios_apps

class DataStore:
    """Data Store class"""
    
    def __init__(self):
        # connect with database MySQL

        mysql_username = 'root'
        mysql_password = ''
        mysql_host = '127.0.0.1:3306'
        mysql_database = 'crawl_data'

        self.engine = create_engine(f'mysql+pymysql://{mysql_username}:{mysql_password}@{mysql_host}/{mysql_database}')
        Base.metadata.create_all(self.engine)

    def make_app(self,data, op_sys):
        if(op_sys == 'ios'):
            app_ = IosApp(
                            app_id=data["app_id"],
                            app_name=data["app_name"],
                            category=data["category"],
                            price = 0.0,
                            provider = data["provider"],
                            description=data["description"],
                            score = data["score"],
                            cnt_rates = data["cnt_rates"],
                            subtitle = data["subtitle"],
                            link = data["link"],
                            img_links = ','.join(data["img_links"])  
                        )
            return app_
        
        app_ = AndroidApp(
                            app_id=data['app_id'],
                            app_name=data['app_name'],
                            category=data['category'],
                            price=data['price'],
                            provider=data['provider'],
                            description=data['description'],
                            developer_email=data['developer_email'],
                        )
        
        return app_


    def insert_values(self, data_list, op_sys):
        with Session(self.engine) as session:
            try:
                
                for data in data_list:
                    try:
                        app_entry = self.make_app(data, op_sys)
                        session.add(app_entry)  
                        session.commit()  

                    except Exception as e:
                        session.rollback()  
                        print(f"Error inserting individual value: {data['app_id']} - {e}")
            
            except Exception as e:
                print(f"General error while processing data_list: {e}")

            finally:
                session.close()

def list_to_string(data):
    """turn list into list"""
    if isinstance(data, list):
        return ' '.join(map(list_to_string, data))  # deque turn element to string
    elif isinstance(data, dict):
        return str(data)  # dictionary to string
    else:
        return str(data)  # other element to string

def extract_quoted_strings(data):
    """extract string inside quote sign"""

    # Regular expression finds all strings within double quotes
    quoted_strings = re.findall(r'"com(.*?)"', data)
    return quoted_strings

def find_list_android_app_ids(language, country, length, chart_name, category_id):
    """find list of android_app's id"""

    url = f'https://play.google.com/_/PlayStoreUi/data/batchexecute?hl={language}&gl={country}'

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
    }

    # Prepare the body similar to the f.req structure in the original request
    body = {
        'f.req': json.dumps([
            [
                [
                    'vyAe2',
                    json.dumps([[None, [[None, [None, length]], None, None, [113]], [2, chart_name, category_id]]])
                ]
            ]
        ])
    }

    response = requests.post(url, headers=headers, data=body)
    response_text = response.text
    if response_text.startswith(")]}'"):
        response_text = response_text[4:]

    # Now try to load the cleaned string
    try:
        json_str = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")

    string_result = list_to_string(json_str)
    quoted_strings = extract_quoted_strings(string_result)
    app_strings = ['com' + link for link in quoted_strings]

    return app_strings

def find_df_ios_app(url):
    """find list of ios_app contain rank, title, subtitle, link, img_links"""

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    top_list = soup.find('ol', role='feed')

    df = pd.DataFrame(columns=['rank', 'title', 'subtitle', 'link', 'img_links'])
    apps_data = top_list.find_all('li')

    for app_data in apps_data:  
        link_tag = app_data.find('a')
        
        # if 'a' tag was founded
        if link_tag:  
            link = link_tag.get('href')
            
            # get images lnk
            images = app_data.find('div').find('picture').find_all('source')
            image_link = [img.get('srcset') for img in images]

            # get rank
            rank = link_tag.find('p', class_='we-lockup__rank').get_text()
            
            # get title
            title = link_tag.find('div', class_='we-lockup__text').find('div', class_='we-lockup__title').find(
                'div',  class_='we-truncate we-truncate--multi-line targeted-link__target'
            ).find('p').get_text()
            
            # get subtitle
            sub_title = link_tag.find('div', class_='we-lockup__text').find('div', class_='we-truncate we-truncate--single-line we-lockup__subtitle').get_text()

            # add data into DataFrame
            temp_df = pd.DataFrame({
                'rank': [rank],
                'title': [title],
                'subtitle': [sub_title],
                'link': [link],
                'img_links': [image_link]
            })
            
            # combine to main data frame
            df = pd.concat([df, temp_df], ignore_index=True)
        else:
            print("Không tìm thấy thẻ <a> với class 'we-lockup  targeted-link'")

    return df
    

def crawl_android(language, country, chart_name, category_id):
    """crawl android apps"""

    #crawl data android app from google play store
    collector = AndroidDataCollector()

    length = 100

    android_app_ids = find_list_android_app_ids(language, country, length, chart_name, category_id)

    collector.collect_android_data(android_app_ids)
    collected_android_apps = collector.get_collected_android_apps()

    #store data

    data_to_store = [{
        "app_id": app.app_id,
        "app_name": app.app_name,
        "category": app.category,
        "price": app.price,
        "provider": app.provider,
        "description": app.description,
        "developer_email": app.developer_email,
    } for app in collected_android_apps]

    
    # Save data to database
    try:
        for data in data_to_store:
            # Check if app_id is not a string
            if not isinstance(data['app_id'], str):  # Use isinstance for type checking
                raise ValueError(f"Invalid type for app_id: {data['app_id']} (type: {type(data['app_id'])})")
    
        # Insert values into the database
        store = DataStore()
        store.insert_values(data_to_store, 'android')

    except Exception as e:  # Catch all exceptions
        print(f"An error occurred: {e}")  # Log the error message
        return data_to_store  # Return the problematic data for further investigation

def main_android():
    crawl_android('en', 'vn', 'topselling_free', 'APPLICATION') #top free
    print("done top free")
    crawl_android('en', 'vn', 'topgrossing', 'APPLICATION') #top grossing
    print("done top grossing")
    crawl_android('en', 'vn', 'topselling_paid', 'APPLICATION') #topselling_paid
    print("done top paid")

def crawl_ios(url):
    """crawl ios apps"""
    
    #crawl data android app from google play store
    collector = IosDataCollector()
    ios_df = find_df_ios_app(url)

    collector.collect_ios_data(ios_df)
    collected_ios_apps = collector.get_collected_ios_apps()
    
    data_to_store = [{
        "app_id": app.app_id,
        "app_name": app.app_name,
        "category": app.category,
        "price": app.price,
        "provider": app.provider,
        "description": app.description,
        "score": app.score,
        "cnt_rates": app.cnt_rates,
        "subtitle": app.subtitle,
        "link": app.link,
        "img_links": app.img_links,
    } for app in collected_ios_apps]

    # Save data to database
    try:
        store = DataStore()
        store.insert_values(data_to_store, 'ios')

    except Exception as e:  # Catch all exceptions
        print(f"An error occurred: {e}")  # Log the error message
        return data_to_store  # Return the problematic data for further investigation

def main_ios():
    url_top_free = 'https://apps.apple.com/vn/charts/iphone/top-free-apps/36'
    url_top_paid = 'https://apps.apple.com/vn/charts/iphone/top-paid-apps/36'

    crawl_ios(url_top_free) #top free
    print("done ios top free")
    crawl_ios(url_top_paid) #top paid
    print("done ios top paid")

if __name__ == "__main__":
    main_android()
    main_ios()