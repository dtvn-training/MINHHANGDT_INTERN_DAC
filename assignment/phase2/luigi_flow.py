import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assignment')))

import re
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
from phase1.code.process.logics.android_data_collector import AndroidDataCollector
from phase1.code.process.logics.ios_data_collector import IosDataCollector
from phase1.code.process.logics.app_service import DataStore
from phase1.code.process.database.database import SessionLocal
import os
import logging
import datetime
import luigi

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

class BaseTask(luigi.Task):
    datehour = luigi.DateHourParameter(default=datetime.datetime.now())
    logger = logging.getLogger(__name__)

    @property
    def cls_name(self):
        return self.__class__.__name__
    
    @property
    def module(self):
        return self.__module__
    
    def run(self):
        self.logger.info("Start %s. [%s]", self.cls_name, self.datehour)

        try:
            self.execute(self.cls_name)
        except Exception as e:
            self.logger.error("Exception. [%s]", e, exc_info=True)
            raise

        self.logger.info("End %s. [%s]", self.cls_name, self.datehour)

    def output(self):
        task_name = "{}.{}".format(self.module, self.cls_name)
        return luigi.LocalTarget(f"output/{task_name}_{self.datehour.strftime("%Y-%m-%d_%H%M")}.txt")
    
    def execute(self, cls_name):
        """ Override this method in the child class to implement specific task logic """
        pass

class FindAndroidData (BaseTask):
    language = luigi.Parameter(default="en")
    country = luigi.Parameter(default="vi")
    chart_name = luigi.Parameter(default="topselling_free")
    length = luigi.IntParameter(default=100)
    category_id = luigi.Parameter(default="APPLICATION")
    url_template = luigi.Parameter(default="https://play.google.com/_/PlayStoreUi/data/batchexecute?hl={language}&gl={country}")
    datehour = luigi.DateHourParameter(default=datetime.datetime.now())

    def execute(self, cls_name):
        url = self.url_template.format(language=self.language, country=self.country)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }

        # Prepare the body similar to the f.req structure in the original request
        body = {
            'f.req': json.dumps([
                [
                    [
                        'vyAe2',
                        json.dumps([[None, [[None, [None, int(self.length) + 50]], None, None, [113]], [2, self.chart_name, self.category_id]]])
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

        app_strings_return = app_strings[:int(self.length)]

        with self.output().open('w') as file:
            for app_string in app_strings_return:
                file.write(app_string + '\n')

class ProcessAndroidData(BaseTask):
    """Crawl Android apps data from Google Play Store"""
    language = luigi.Parameter(default="en")
    country = luigi.Parameter(default="vi")
    chart_name = luigi.Parameter(default="topselling_free")
    length = luigi.IntParameter(default=100)
    category_id = luigi.Parameter(default="APPLICATION")
    datehour = luigi.DateHourParameter(default=datetime.datetime.now())

    def requires(self):
        return [FindAndroidData(self.language, self.country, self.chart_name, self.length, self.category_id)]
    
    def execute(self, cls_name):
        try: 
            collector = AndroidDataCollector()
            # `self.input()` returns a list, so access the first item
            with self.input()[0].open('r') as input_file:
                android_app_ids = input_file.read().splitlines()  # ensure it's a list of app IDs
            collector.collect_android_data(android_app_ids)
            collected_android_apps = collector.get_collected_android_apps()

            data_to_store = [{
                "app_id": app.app_id,
                "app_name": app.app_name,
                "category": app.category,
                "price": app.price,
                "provider": app.provider,
                "description": app.description,
                "developer_email": app.developer_email,
            } for app in collected_android_apps]

            # Lưu dữ liệu vào cơ sở dữ liệu
            session = SessionLocal()
            store = DataStore(session)
            store.insert_values(data_to_store, 'android')

            # Lưu dữ liệu vào file đầu ra (nếu cần)
            with self.output().open('w') as output_file:
                import json
                json.dump(data_to_store, output_file)

            self.logger.info(f"Successfully crawled and stored Android data to {self.output().path}")

        except Exception as e:
            self.logger.info(f"Errorly crawled and stored Android data to {self.output().path}")
            return None

class FindIosData(BaseTask):
    url = luigi.Parameter()

    def output(self):
        # Ensure the 'output' directory exists
        os.makedirs('output', exist_ok=True)  # Creates the directory if it doesn't exist
        
        task_name = "{}.{}".format(self.module, self.cls_name)
        return luigi.LocalTarget(f"output/{task_name}_{self.datehour.strftime('%Y-%m-%d_%H%M')}.csv")
    
        # Define the output, which could be a file or database entry
        # return luigi.LocalTarget(f"{self.url.split('/')[-1]}.csv")

    def execute(self, cls_name):
        """Fetch the iOS app data and save it to CSV"""
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')

        top_list = soup.find('ol', role='feed')

        df = pd.DataFrame(columns=['rank', 'title', 'subtitle', 'link', 'img_links'])
        apps_data = top_list.find_all('li')

        for app_data in apps_data:
            link_tag = app_data.find('a')
            if link_tag:
                link = link_tag.get('href')
                images = app_data.find('div').find('picture').find_all('source')
                image_link = [img.get('srcset') for img in images]
                rank = link_tag.find('p', class_='we-lockup__rank').get_text()
                title = link_tag.find('div', class_='we-lockup__text').find('div', class_='we-lockup__title').find(
                    'div', class_='we-truncate we-truncate--multi-line targeted-link__target'
                ).find('p').get_text()
                sub_title = link_tag.find('div', class_='we-lockup__text').find('div', class_='we-truncate we-truncate--single-line we-lockup__subtitle').get_text()

                temp_df = pd.DataFrame({
                    'rank': [rank],
                    'title': [title],
                    'subtitle': [sub_title],
                    'link': [link],
                    'img_links': [image_link]
                })

                df = pd.concat([df, temp_df], ignore_index=True)
            else:
                print("Không tìm thấy thẻ <a> với class 'we-lockup  targeted-link'")

        # Save to CSV
        df.to_csv(self.output().path, index=False)

class ProcessIosData(BaseTask):
    url = luigi.Parameter()

    def requires(self):
        return FindIosData(url=self.url)
    
    def output(self):
        # Ensure the 'output' directory exists
        os.makedirs('output', exist_ok=True)  # Creates the directory if it doesn't exist
        
        task_name = "{}.{}".format(self.module, self.cls_name)
        return luigi.LocalTarget(f"output/{task_name}_{self.datehour.strftime('%Y-%m-%d_%H%M')}.csv")
    
        # Define the output file path, for example:
        # return luigi.LocalTarget(f"processed_{self.url.split('/')[-1]}.csv")

    def execute(self, cls_name):
        """Process the data, collect it using IosDataCollector, and insert into DB"""
        collector = IosDataCollector()
        ios_df = pd.read_csv(self.input().path)

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

        # Store data in database
        session = SessionLocal()  # Initialize your session correctly
        store = DataStore(session)
        store.insert_values(data_to_store, 'ios')

        # Save processed data to output file
        processed_data_df = pd.DataFrame(data_to_store)
        processed_data_df.to_csv(self.output().path, index=False)

        self.logger.info(f"Successfully crawled and stored {len(data_to_store)} iOS apps.")

class RunAllAndroidTasks(luigi.WrapperTask):
    def requires(self):
        yield ProcessAndroidData(language="en", country="vi", chart_name="topselling_free", length=100, category_id="APPLICATION")
        yield ProcessAndroidData(language="en", country="vi", chart_name="topgrossing", length=100, category_id="APPLICATION")
        yield ProcessAndroidData(language="en", country="vi", chart_name="topselling_paid", length=100, category_id="APPLICATION")

class RunAllIosTasks(luigi.WrapperTask):
    def requires(self):
        yield ProcessIosData(url="https://apps.apple.com/vn/charts/iphone/top-free-apps/36")
        yield ProcessIosData(url="https://apps.apple.com/vn/charts/iphone/top-paid-apps/36")
        
class RunAllTasks(luigi.WrapperTask):
    def requires(self):
        yield ProcessAndroidData(language="en", country="vi", chart_name="topselling_free", length=100, category_id="APPLICATION")
        yield ProcessAndroidData(language="en", country="vi", chart_name="topgrossing", length=100, category_id="APPLICATION")
        yield ProcessAndroidData(language="en", country="vi", chart_name="topselling_paid", length=100, category_id="APPLICATION")

        yield ProcessIosData(url="https://apps.apple.com/vn/charts/iphone/top-free-apps/36")
        yield ProcessIosData(url="https://apps.apple.com/vn/charts/iphone/top-paid-apps/36")


