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
    DRYRUN = luigi.BoolParameter(default = True)

    def execute(self, cls_name):
        if self.DRYRUN:
            # Chế độ dry-run: Chỉ log và không thực hiện hành động thật
            logging.info("[DRYRUN] Simulating find android data")
            android_app_ids = ['com.example.app1', 'com.example.app2', 'com.example.app3']

            target_file = self.output().path
            if os.path.exists(target_file):
                self.logger.warning(f"File {target_file} already exists. Renaming or deleting it.")
                os.remove(target_file)  # Or you can rename the file

            with self.output().open('w') as f:
                for app_string in android_app_ids:
                    f.write(app_string + '\n')
            return

        run_find_android_data(self.output().path, self.chart_name, self.length)

class ProcessAndroidData(BaseTask):
    """Crawl Android apps data from Google Play Store"""
    chart_name = luigi.Parameter(default="topselling_free")
    length = luigi.IntParameter(default=100)
    DRYRUN = luigi.BoolParameter(default=True)
    datehour = luigi.DateHourParameter(default=datetime.datetime.now())

    def requires(self):
        return [FindAndroidData(self.chart_name, self.length, DRYRUN = self.DRYRUN)]
    
    def execute(self, cls_name):
        if self.DRYRUN:
            
            target_file = self.output().path
            if os.path.exists(target_file):
                self.logger.warning(f"File {target_file} already exists. Renaming or deleting it.")
                os.remove(target_file)  # Or you can rename the file

            # Chế độ dry-run: Chỉ log và không thực hiện hành động thật
            logging.info("[DRYRUN] Simulating data processing for iOS app")
            with self.input()[0].open('r') as input_file:
                    android_app_ids = input_file.read().splitlines()
            with self.output().open('w') as f:
                f.write('Simulated data processing completed: ' + ', '.join(android_app_ids))
            return
        
        try: 
            run_process_android_data(self.input()[0].path, self.output().path)

            self.logger.info(f"Successfully crawled and stored Android data to {self.output().path}")

        except Exception as e:
            self.logger.info(f"Errorly crawled and stored Android data to {self.output().path}")
            return None

class FindIosData(BaseTask):
    url = luigi.Parameter()
    DRYRUN = luigi.BoolParameter(default=True)

    def output(self):
        # Ensure the 'output' directory exists
        os.makedirs('output_ios', exist_ok=True)  # Creates the directory if it doesn't exist
        
        # Define the output, which could be a file or database entry
        task_name = "{}.{}".format(self.module, self.cls_name)
        return luigi.LocalTarget(f"output_ios/{task_name}_{self.datehour.strftime('%Y-%m-%d_%H%M')}.csv")
    
    def execute(self, cls_name):
        if self.DRYRUN:
            # Chế độ dry-run: Chỉ log và không thực hiện hành động thật
            logging.info("[DRYRUN] Simulating find IOS data")
            ios_df = pd.DataFrame({
                'rank': [1],
                'title': ['ios_app1'],
                'subtitle': ['this is ios app 1'],
                'link': ['example1.com'],
                'img_links': ['img1.com']
            },
            {
                'rank': [2],
                'title': ['ios_app2'],
                'subtitle': ['this is ios app 2'],
                'link': ['example2.com'],
                'img_links': ['img2.com']
            },
            {
                'rank': [3],
                'title': ['ios_app3'],
                'subtitle': ['this is ios app 3'],
                'link': ['example3.com'],
                'img_links': ['img3.com']
            })

            target_file = self.output().path
            if os.path.exists(target_file):
                self.logger.warning(f"File {target_file} already exists. Renaming or deleting it.")
                os.remove(target_file)  # Or you can rename the file

            ios_df.to_csv(self.output().path, index = False)
            return
        
        df = find_df_ios_app(self.url)
        # Save to CSV
        df.to_csv(self.output().path, index=False)

class ProcessIosData(BaseTask):
    url = luigi.Parameter()
    DRYRUN = luigi.BoolParameter(default=True)

    def requires(self):
        return FindIosData(url=self.url, DRYRUN = self.DRYRUN)
    
    def output(self):
        # Ensure the 'output' directory exists
        os.makedirs('output_ios', exist_ok=True)  # Creates the directory if it doesn't exist
        
        task_name = "{}.{}".format(self.module, self.cls_name)
        return luigi.LocalTarget(f"output_ios/{task_name}_{self.datehour.strftime('%Y-%m-%d_%H%M')}.csv")

    def execute(self, cls_name):
        if self.DRYRUN:
            
            target_file = self.output().path
            if os.path.exists(target_file):
                self.logger.warning(f"File {target_file} already exists. Renaming or deleting it.")
                os.remove(target_file)  # Or you can rename the file
                
            # Chế độ dry-run: Chỉ log và không thực hiện hành động thật
            logging.info("[DRYRUN] Simulating data processing for iOS app")
            ios_df = pd.read_csv(self.input().path)
            processed_data_df = pd.DataFrame(ios_df)
            processed_data_df.to_csv(self.output().path, index=False)
            return
        
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
    DRYRUN = luigi.BoolParameter(default=True)
    def requires(self):
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
    # luigi.build([RunAllAndroidTasks()], local_scheduler = True)
    # luigi.build([RunAllIosTasks()], local_scheduler = True)
    luigi.build([RunAllTasks(DRYRUN = False)], local_scheduler = True)