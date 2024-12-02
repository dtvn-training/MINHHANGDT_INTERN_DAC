import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assignment')))
import pandas as pd
from phase1.code.process.logics.execute import run_process_android_data,run_find_android_data, get_android_ids, find_df_ios_app ,process_android_data, process_ios_data, run_process_ios_data
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

        target_path = f"output_android/{task_name}_{self.datehour.strftime("%Y-%m-%d_%H%M")}.txt"
        return luigi.LocalTarget(target_path)
    
    def execute(self, cls_name):
        """ Override this method in the child class to implement specific task logic """
        pass

class FindAndroidData (BaseTask):
    chart_name = luigi.Parameter(default="topselling_free")
    length = luigi.IntParameter(default=100)
    datehour = luigi.DateHourParameter(default=datetime.datetime.now())

    def execute(self, cls_name):
        run_find_android_data(self.output().path, self.chart_name, self.length)

class ProcessAndroidData(BaseTask):
    """Crawl Android apps data from Google Play Store"""
    chart_name = luigi.Parameter(default="topselling_free")
    length = luigi.IntParameter(default=100)
    datehour = luigi.DateHourParameter(default=datetime.datetime.now())

    def requires(self):
        return [FindAndroidData(self.chart_name, self.length)]
    
    def execute(self, cls_name):
        try: 
            run_process_android_data(self.input()[0].path, self.output().path)

            self.logger.info(f"Successfully crawled and stored Android data to {self.output().path}")

        except Exception as e:
            self.logger.info(f"Errorly crawled and stored Android data to {self.output().path}")
            return None

class FindIosData(BaseTask):
    url = luigi.Parameter()

    def output(self):
        # Ensure the 'output' directory exists
        os.makedirs('output_ios', exist_ok=True)  # Creates the directory if it doesn't exist
        
        # Define the output, which could be a file or database entry
        task_name = "{}.{}".format(self.module, self.cls_name)
        return luigi.LocalTarget(f"output_ios/{task_name}_{self.datehour.strftime('%Y-%m-%d_%H%M')}.csv")
    
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
        os.makedirs('output_ios', exist_ok=True)  # Creates the directory if it doesn't exist
        
        task_name = "{}.{}".format(self.module, self.cls_name)
        return luigi.LocalTarget(f"output_ios/{task_name}_{self.datehour.strftime('%Y-%m-%d_%H%M')}.csv")

    def execute(self, cls_name):
        """Process the data, collect it using IosDataCollector, and insert into DB"""
        run_process_ios_data(self.input().path, self.output().path)
        # self.logger.info(f"Successfully crawled and stored {len(data_to_store)} iOS apps.")
        self.logger.info(f"Successfully crawled and stored iOS apps.")

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
