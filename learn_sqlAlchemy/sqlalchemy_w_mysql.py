from abc import ABC, abstractmethod
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.declarative import declared_attr

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

    app_id = Column(String(1000), primary_key=True)
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

        mysql_username = ''
        mysql_password = ''
        mysql_host = ''
        mysql_database = ''

        self.engine = create_engine(f'mysql+pymysql://{mysql_username}:{mysql_password}@{mysql_host}/{mysql_database}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def insert_values(self):
        # print("data_list ", data_list)
        session = self.Session()

        try:
            # Kiểm tra kết nối tới MySQL
            conn = self.engine.connect()
            print("Kết nối thành công!")
            conn.close()
        except Exception as e:
            print(f"Không thể kết nối tới MySQL: {e}")

           
        try:
            app_entry = AndroidApp(
                app_id='com.chatgpt',
                app_name='chat gpt',
                category='tool',
                price=0.0,
                provider='openai',
                description='hello world',
                developer_email='e@gmail.com',
            )
            session.add(app_entry)  
            session.commit()  

        except Exception as e:
            session.rollback()  
            print(f"Error: {e}")

        finally:
            session.close()

ds = DataStore()
ds.insert_values()