import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assignment')))
import pandas as pd
from phase1.code.process.logics.execute import run_process_android_data,run_find_android_data, get_android_ids, find_df_ios_app ,process_android_data, process_ios_data, run_process_ios_data
import os
import logging
import datetime
import luigi
from phase1.code.process.database.database import init_db

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
    DRYRUN = luigi.BoolParameter(default = False)

    def execute(self, cls_name):
        run_find_android_data(self.output().path, self.chart_name, self.length, self.DRYRUN)

class ProcessAndroidData(BaseTask):
    """Crawl Android apps data from Google Play Store"""
    chart_name = luigi.Parameter(default="topselling_free")
    length = luigi.IntParameter(default=100)
    DRYRUN = luigi.BoolParameter(default=False)
    datehour = luigi.DateHourParameter(default=datetime.datetime.now())

    def requires(self):
        return [FindAndroidData(self.chart_name, self.length, DRYRUN = self.DRYRUN)]
    
    def execute(self, cls_name):
        try: 
            run_process_android_data(self.input()[0].path, self.output().path, self.DRYRUN)

            self.logger.info(f"Successfully crawled and stored Android data to {self.output().path}")

        except Exception as e:
            self.logger.info(f"Errorly crawled and stored Android data to {self.output().path}")
            return None

class FindIosData(BaseTask):
    url = luigi.Parameter()
    DRYRUN = luigi.BoolParameter(default=False)

    def output(self):
        # Ensure the 'output' directory exists
        os.makedirs('output_ios', exist_ok=True)  # Creates the directory if it doesn't exist
        
        # Define the output, which could be a file or database entry
        task_name = "{}.{}".format(self.module, self.cls_name)
        return luigi.LocalTarget(f"output_ios/{task_name}_{self.datehour.strftime('%Y-%m-%d_%H%M')}.csv")
    
    def execute(self, cls_name):
        target_file = self.output().path
        if os.path.exists(target_file):
            self.logger.warning(f"File {target_file} already exists. Renaming or deleting it.")
            os.remove(target_file)  # Or you can rename the file
    
        df = find_df_ios_app(self.url, self.DRYRUN)
        # Save to CSV
        df.to_csv(self.output().path, encoding="utf-8", index=False)

class ProcessIosData(BaseTask):
    url = luigi.Parameter()
    DRYRUN = luigi.BoolParameter(default=False)

    def requires(self):
        return FindIosData(url=self.url, DRYRUN = self.DRYRUN)
    
    def output(self):
        # Ensure the 'output' directory exists
        os.makedirs('output_ios', exist_ok=True)  # Creates the directory if it doesn't exist
        
        task_name = "{}.{}".format(self.module, self.cls_name)
        return luigi.LocalTarget(f"output_ios/{task_name}_{self.datehour.strftime('%Y-%m-%d_%H%M')}.csv")

    def execute(self, cls_name):
        
        """Process the data, collect it using IosDataCollector, and insert into DB"""
        run_process_ios_data(self.input().path, self.output().path, self.DRYRUN)
        # self.logger.info(f"Successfully crawled and stored {len(data_to_store)} iOS apps.")
        self.logger.info(f"Successfully crawled and stored iOS apps.")

class RunAllAndroidTasks(luigi.WrapperTask):
    DRYRUN = luigi.BoolParameter(default=False)
    def requires(self):
        yield ProcessAndroidData(chart_name="topselling_free", length=100, DRYRUN = self.DRYRUN)
        yield ProcessAndroidData(chart_name="topgrossing", length=100, DRYRUN = self.DRYRUN)
        yield ProcessAndroidData(chart_name="topselling_paid", length=100, DRYRUN = self.DRYRUN)

class RunAllIosTasks(luigi.WrapperTask):
    DRYRUN = luigi.BoolParameter(default=False)
    def requires(self):
        yield ProcessIosData(url="https://apps.apple.com/vn/charts/iphone/top-free-apps/36", DRYRUN = self.DRYRUN)
        yield ProcessIosData(url="https://apps.apple.com/vn/charts/iphone/top-paid-apps/36", DRYRUN = self.DRYRUN)
        
class RunAllTasks(luigi.WrapperTask):
    DRYRUN = luigi.BoolParameter(default=False)
    def requires(self):
        init_db()
        yield ProcessAndroidData(chart_name="topselling_free", length=100, DRYRUN = self.DRYRUN)
        yield ProcessAndroidData(chart_name="topgrossing", length=100, DRYRUN = self.DRYRUN)
        yield ProcessAndroidData(chart_name="topselling_paid", length=100, DRYRUN = self.DRYRUN)
        yield ProcessIosData(url="https://apps.apple.com/vn/charts/iphone/top-free-apps/36", DRYRUN = self.DRYRUN)
        yield ProcessIosData(url="https://apps.apple.com/vn/charts/iphone/top-paid-apps/36", DRYRUN = self.DRYRUN)

# if __name__ == '__main__':
#     luigi.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
    # luigi.build([RunAllAndroidTasks(DRYRUN = True)], local_scheduler = True)
    # luigi.build([RunAllIosTasks(DRYRUN = False)], local_scheduler = True)
    luigi.build([RunAllTasks(DRYRUN = False)], local_scheduler = True)
