import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assignment')))

# from assignment.phase1.code.process.database.database import init_db
from phase1.code.process.database.database import init_db
import luigi
from phase2.luigi_flow import RunAllAndroidTasks, RunAllIosTasks, RunAllTasks
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
    # luigi.build([RunAllAndroidTasks()], local_scheduler = True)
    # luigi.build([RunAllIosTasks()], local_scheduler = True)
    luigi.build([RunAllTasks()], local_scheduler = True)
