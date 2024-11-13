import os

class Config:
    mysql_username = 'root'
    mysql_password = 'HIn-129cpdatadac'
    mysql_host = '127.0.0.1:3306'
    mysql_database = 'crawl_data'

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{mysql_username}:{mysql_password}@{mysql_host}/{mysql_database}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False