import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assignment')))
import pandas as pd
from phase1.code.process.logics.execute import get_android_ids, find_df_ios_app ,process_android_data, process_ios_data
import os
import logging
import datetime
import luigi

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
    chart_name = luigi.Parameter(default="topselling_free")
    length = luigi.IntParameter(default=100)
    datehour = luigi.DateHourParameter(default=datetime.datetime.now())

    def execute(self, cls_name):
        app_strings_return = get_android_ids(self.chart_name, self.length)
        
        with self.output().open('w') as file:
            for app_string in app_strings_return:
                file.write(app_string + '\n')

class ProcessAndroidData(BaseTask):
    """Crawl Android apps data from Google Play Store"""
    chart_name = luigi.Parameter(default="topselling_free")
    length = luigi.IntParameter(default=100)
    datehour = luigi.DateHourParameter(default=datetime.datetime.now())

    def requires(self):
        return [FindAndroidData(self.chart_name, self.length)]
    
    def execute(self, cls_name):
        try: 
            # `self.input()` returns a list, so access the first item
            with self.input()[0].open('r') as input_file:
                android_app_ids = input_file.read().splitlines()  # ensure it's a list of app IDs
            data_to_store = process_android_data(android_app_ids)
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
        
        # Define the output, which could be a file or database entry
        task_name = "{}.{}".format(self.module, self.cls_name)
        return luigi.LocalTarget(f"output/{task_name}_{self.datehour.strftime('%Y-%m-%d_%H%M')}.csv")
    
    def execute(self, cls_name):
        df = find_df_ios_app(self.url)
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
        ios_df = pd.read_csv(self.input().path)
        data_to_store = process_ios_data(ios_df)

        # Save processed data to output file
        processed_data_df = pd.DataFrame(data_to_store)
        processed_data_df.to_csv(self.output().path, index=False)

        self.logger.info(f"Successfully crawled and stored {len(data_to_store)} iOS apps.")

class RunAllAndroidTasks(luigi.WrapperTask):
    def requires(self):
        yield ProcessAndroidData(chart_name="topselling_free", length=100)
        yield ProcessAndroidData(chart_name="topgrossing", length=100)
        yield ProcessAndroidData(chart_name="topselling_paid", length=100)

class RunAllIosTasks(luigi.WrapperTask):
    def requires(self):
        yield ProcessIosData(url="https://apps.apple.com/vn/charts/iphone/top-free-apps/36")
        yield ProcessIosData(url="https://apps.apple.com/vn/charts/iphone/top-paid-apps/36")
        
class RunAllTasks(luigi.WrapperTask):
    def requires(self):
        yield ProcessAndroidData(chart_name="topselling_free", length=100)
        yield ProcessAndroidData(chart_name="topgrossing", length=100)
        yield ProcessAndroidData(chart_name="topselling_paid", length=100)
        yield ProcessIosData(url="https://apps.apple.com/vn/charts/iphone/top-free-apps/36")
        yield ProcessIosData(url="https://apps.apple.com/vn/charts/iphone/top-paid-apps/36")
