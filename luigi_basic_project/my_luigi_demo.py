import luigi
import datetime
import os

#basic task with local target
class GenerateData(luigi.Task):
    date = luigi.DateParameter(default=datetime.date(2024, 10, 22))
    int_param = luigi.IntParameter(default=10)
    
    def output(self):
        return luigi.LocalTarget(f"data/output_{self.date}_{self.int_param}.txt")
    
    def run(self):
        with self.output().open('w') as f:
            f.write(f"Generated data for date: {self.date}, with int_param: {self.int_param}\n")

#task that require other task
#depend on Generate Data (use requires)
#read output from GenerateData and process, save result in other file
#use param datehour and string_param
class ProcessData(luigi.Task):
    date = luigi.DateParameter(default=datetime.date(2024, 10, 22))
    datehour = luigi.DateHourParameter(default=datetime.datetime(2024, 10, 22, 14))
    string_param = luigi.Parameter(default = "HelloWorld")
    int_param = luigi.IntParameter(default=10)

    def requires(self):
        return [GenerateData(date = self.date, int_param = self.int_param)]
    
    def output(self):
        formatted_datehour = self.datehour.strftime("%Y-%m-%d_%H%M")
        return luigi.LocalTarget(f"data/process_{formatted_datehour}_{self.string_param}.txt")
    
    def run(self):
        with self.input()[0].open('r') as input_file:
            data = input_file.read()
        with self.output().open('w') as output_file:
            output_file.write(f"Processed data for datehour: {self.datehour}, string_param: {self.string_param}\n")
            output_file.write(f"Data from GenerateData: {data}")

#WrapperTask cover many tasks
#Integrate tasks together, make convenient management
class DataPipeLine(luigi.WrapperTask):
    date = luigi.DateParameter(default=datetime.date(2024, 10, 22))
    datehour = luigi.DateHourParameter(default=datetime.datetime(2024, 10, 22, 14))
    string_param = luigi.Parameter(default="HelloWorld")
    int_param = luigi.IntParameter(default=10)

    def requires(self):
        return [ProcessData(date=self.date, datehour=self.datehour, string_param=self.string_param, int_param=self.int_param)]
    

if __name__ == "__main__":
    # luigi.build([DataPipeLine(date='2024-10-22', datehour='2024-10-22T15', string_param="DemoRun", int_param=42)], local_schedule=True)
    # luigi.build([GenerateData(date=datetime.date(2024, 10, 22), int_param = 42)], local_scheduler=True)
    luigi.build([DataPipeLine(date=datetime.date(2024, 10, 22), datehour = datetime.datetime(2024, 10, 22, 14), string_param = "HelloDAC", int_param = 42)], local_scheduler=True)

