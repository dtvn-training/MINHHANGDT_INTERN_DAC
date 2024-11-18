import sys
import os

# Add the root directory of the project to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import unittest
from unittest.mock import patch
from process.logics.android_data_collector import AndroidDataCollector


class TestAndroidDataCollector(unittest.TestCase):

    @patch('logics.collectors.android_data_collector.app') #Mock app function from google_play_scraper
    def test_collect_android_data_success(self, mock_app):
        #Arrange
        mock_app.side_effect = [
            {
                "title": "App One",
                "genre": "Application",
                "price": "0",
                "developer": "Provider One",
                "description": "App One Description",
                "developerEmail": "dev1@example.com"
            },
            {
                "title": "App Two",
                "genre": "Productivity",
                "price": "1.99",
                "developer": "Provider Two",
                "description": "App Two Description",
                "developerEmail": "dev2@example.com"
            }
        ] #Simulate return data of app function

        collector = AndroidDataCollector()
        app_ids = ['app1', 'app2']

        #Act
        collector.collect_android_data(app_ids)

        #Assert
        collected_apps = collector.get_collected_android_apps()
        self.assertEqual(len(collected_apps), 2)

        # Check first app
        self.assertEqual(collected_apps[0].app_id, 'app1')
        self.assertEqual(collected_apps[0].app_name, 'App One')
        self.assertEqual(collected_apps[0].category, 'Application')
        self.assertEqual(collected_apps[0].price, 0.0)
        self.assertEqual(collected_apps[0].provider, 'Provider One')
        self.assertEqual(collected_apps[0].description, 'App One Description')
        self.assertEqual(collected_apps[0].developer_email, 'dev1@example.com')

        # Check second app
        self.assertEqual(collected_apps[1].app_id, 'app2')
        self.assertEqual(collected_apps[1].app_name, 'App Two')
        self.assertEqual(collected_apps[1].category, 'Productivity')
        self.assertEqual(collected_apps[1].price, 1.99)
        self.assertEqual(collected_apps[1].provider, 'Provider Two')
        self.assertEqual(collected_apps[1].description, 'App Two Description')
        self.assertEqual(collected_apps[1].developer_email, 'dev2@example.com')

    @patch('logics.collectors.android_data_collector.app')
    def test_collector_data_failure(self, mock_app):
        #Arrange
        mock_app.side_effect = Exception("Test Exception") #Simulate error when crawl data

        collector = AndroidDataCollector()
        app_ids = ['app1', 'app2']

        #Act
        collector.collect_android_data(app_ids)

        #Assert
        collected_apps = collector.get_collected_android_apps()
        self.assertEqual(len(collected_apps), 0) #Error happen, no app be crawled
        print("Test case for failure handled successfully")
        
if __name__ == "__main__":
    unittest.main()