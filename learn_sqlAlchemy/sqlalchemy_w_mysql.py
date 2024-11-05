from abc import ABC, abstractmethod
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.exc import SQLAlchemyError

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

class DataStore:
    def __init__(self):
        # Kết nối với cơ sở dữ liệu MySQL

        mysql_username = 'root'
        mysql_password = ''
        mysql_host = '127.0.0.1:3306'
        mysql_database = 'crawl_data'

        self.engine = create_engine(f'mysql+pymysql://{mysql_username}:{mysql_password}@{mysql_host}/{mysql_database}')
        #create table if not exist
        Base.metadata.create_all(self.engine)

    def insert_values(self):
         
         with Session(self.engine) as session:
            try:
                # add new data to table AndroidApp
                app_entry = AndroidApp(
                    app_id='com.chatgpt2',
                    app_name='ChatGPT2',
                    category='tool',
                    price=0.0,
                    provider='OpenAI',
                    description='An AI-based chatbot',
                    developer_email='support@openai.com',
                )
                session.add(app_entry)  # add new record to session
                session.commit()  # save change into database

                app_androids = session.query(AndroidApp).all()
                for app in app_androids:
                    print(f"App ID: {app.app_id}, Name: {app.app_name}, Description: {app.description}")

            except SQLAlchemyError as e:
                session.rollback()  # Rollback 
                print(f"Error: {e}")

            finally:
                session.close()  # close session

ds = DataStore()
ds.insert_values()