
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'code')))

import unittest
from unittest.mock import patch, MagicMock
import json
import requests

from process.logics.wrapper import list_to_string, extract_quoted_strings, find_list_android_app_ids, find_df_ios_app, crawl_android, crawl_ios
from process.logics.app_service import is_record_exists, clean_data

class TestFunctions(unittest.TestCase):
    def test_list_to_string_with_list(self):
        #Arrange
        data = ['hello', 'world']
        expected_output = 'hello world'

        #Act
        result = list_to_string(data)

        #Assert
        self.assertEqual(result, expected_output)

    def test_list_to_string_with_dict(self):
        #Arrange
        data = {'key': 'value'}
        expected_output = "{'key': 'value'}"

        #Act
        result = list_to_string(data)

        #Assert
        self.assertEqual(result, expected_output)

    def test_list_to_string_with_string(self):
        #Arrange
        data = 'hello'
        expected_output = 'hello'

        #Act
        result = list_to_string(data)

        #Assert
        self.assertEqual(result, expected_output)

    def test_extract_quoted_strings(self):
        #Arrange
        data = 'This is a test "com.example" string "com.example2" and "com.example3"'
        expected_output = ['.example', '.example2', '.example3']

        #Act
        result = extract_quoted_strings(data)
        
        #Assert
        self.assertEqual(result, expected_output)

    # @patch('requests.get')
    # def test_find_df_ios_app(self, mock_get):
    #     # Arrange
    #     url = 'https://example.com'
    #     mock_response = MagicMock()
    #     mock_response.text = '''
    #         <html>
    #             <ol role="feed">
    #                 <li>
    #                     <a href="/app_link">
    #                         <p class="we-lockup__rank">1</p>
    #                         <div class="we-lockup__text">
    #                             <div class="we-lockup__title">
    #                                 <div class="we-truncate">
    #                                     <p>App Title</p>
    #                                 </div>
    #                             </div>
    #                             <div class="we-lockup__subtitle">App Subtitle</div>
    #                         </div>
    #                     </a>
    #                     <div>
    #                         <picture>
    #                             <source srcset="img_link_1x">
    #                             <source srcset="img_link_2x">
    #                         </picture>
    #                     </div>
    #                 </li>
    #             </ol>
    #         </html>
    #     '''
    #     mock_get.return_value = mock_response

    #     expected_output_columns = ['rank', 'title', 'subtitle', 'link', 'img_links']

    #     # Act
    #     result_df = find_df_ios_app(url)

    #     # Assert
    #     self.assertEqual(result_df.columns.tolist(), expected_output_columns)
    #     self.assertEqual(result_df['rank'].iloc[0], '1')
    #     self.assertEqual(result_df['title'].iloc[0], 'App Title')
    #     self.assertEqual(result_df['subtitle'].iloc[0], 'App Subtitle')
    #     self.assertEqual(result_df['link'].iloc[0], '/app_link')
    #     self.assertEqual(result_df['img_links'].iloc[0], ['img_link_1x', 'img_link_2x'])

    @patch('process.models.android_app.AndroidApp')
    def test_is_record_exists_android(self, mock_AndroidApp):
        # Arrange
        session = MagicMock()
        app_id = 'com.app1'
        session.query().filter().first.return_value = None

        # Act
        result = is_record_exists(session, app_id, 'android')

        # Assert
        session.query.assert_called_once()
        self.assertFalse(result)@patch('process.models.android_app.AndroidApp')

    @patch('process.models.android_app.AndroidApp')
    def test_is_record_exists_android(self, mock_AndroidApp):
        # Arrange
        session = MagicMock()
        app_id = 'com.app1'
        session.query().filter().first.return_value = None

        # Act
        result = is_record_exists(session, app_id, 'android')

        # Assert
        session.query.assert_called()  # Allow for multiple calls
        self.assertFalse(result)

    def test_is_record_exists_ios(self):
        #Arrange
        session = MagicMock()
        app_id = 'com.app1'

        session.query.return_value.filter.return_value.first.return_value = None

        #Act
        result = is_record_exists(session, app_id, 'ios')

        #Assert
        session.query.assert_called_once()
        self.assertFalse(result)

    def test_clean_data(self):
        #Arrange
        data_list = [{'app_id': 'com.app1'}, {'app_id': 'com.app2'}, {'app_id': 'com.app2'}]
        session = MagicMock()
        op_sys = 'android'

        # Mock the behavior of querying the database
        session.query.return_value.filter.return_value.first.side_effect = [None, None, 'existing_record']

        expected_output = [{'app_id': 'com.app1'}, {'app_id': 'com.app2'}]
        #Act
        result = clean_data(data_list, session, op_sys)

        #Assert
        self.assertEqual(result, expected_output)

class TestCrawlAndroid(unittest.TestCase):
    @patch('process.logics.wrapper.SessionLocal')
    @patch('process.logics.wrapper.AndroidDataCollector')
    @patch('process.logics.wrapper.find_list_android_app_ids')  # Correct the patch path here
    def test_crawl_android_success(self, mock_find_list_android_app_ids, mock_AndroidDataCollector, mock_SessionLocal):
        # Arrange
        # Mock the AndroidDataCollector methods
        mock_collector = MagicMock()
        mock_AndroidDataCollector.return_value = mock_collector

        # Create a list of mock Android app objects
        mock_android_apps = [
            MagicMock(app_id="app_1", app_name="App One", category="Games", price="Free", provider="Provider One",
                      description="Description One", developer_email="devone@example.com"),
            MagicMock(app_id="app_2", app_name="App Two", category="Tools", price="Paid", provider="Provider Two",
                      description="Description Two", developer_email="devtwo@example.com")
        ]

        mock_collector.get_collected_android_apps.return_value = mock_android_apps

        # Mock the list of app IDs returned by find_list_android_app_ids
        mock_find_list_android_app_ids.return_value = ["app_1", "app_2"]

        # Mock the database session and DataStore
        mock_session = MagicMock()
        mock_SessionLocal.return_value = mock_session
        mock_store = MagicMock()

        with patch('process.logics.app_service.DataStore.insert_values') as mock_insert_values:
            # Act
            result = crawl_android('en', 'vn', 'topselling_free', 'APPLICATION', 100)
            
            # Assert
            mock_find_list_android_app_ids.assert_called_once_with('en', 'vn', 100, 'topselling_free', 'APPLICATION')
            mock_collector.collect_android_data.assert_called_once_with(["app_1", "app_2"])
            mock_collector.get_collected_android_apps.assert_called_once()
            mock_SessionLocal.assert_called_once()
            mock_insert_values.assert_called_once_with([
                {
                    "app_id": "app_1",
                    "app_name": "App One",
                    "category": "Games",
                    "price": "Free",
                    "provider": "Provider One",
                    "description": "Description One",
                    "developer_email": "devone@example.com"
                },
                {
                    "app_id": "app_2",
                    "app_name": "App Two",
                    "category": "Tools",
                    "price": "Paid",
                    "provider": "Provider Two",
                    "description": "Description Two",
                    "developer_email": "devtwo@example.com"
                }
            ], 'android')
            self.assertIsNone(result)

    @patch('process.logics.wrapper.SessionLocal')
    @patch('process.logics.android_data_collector.AndroidDataCollector')
    @patch('process.logics.wrapper.find_list_android_app_ids')  # Correct the patch path here
    def test_crawl_android_failure(self, mock_find_list_android_app_ids, mock_AndroidDataCollector, mock_SessionLocal):
        # Arrange
        # Simulate an exception during data collection
        mock_collector = MagicMock()
        mock_AndroidDataCollector.return_value = mock_collector
        mock_collector.collect_android_data.side_effect = Exception("Test error")

        mock_find_list_android_app_ids.return_value = ["app_1", "app_2"]

        # Act
        result = crawl_android('en', 'vn', 'topselling_free', 'APPLICATION', 100)

        # Assert
        self.assertIsNone(result)

if __name__=="__main__":
    unittest.main()
