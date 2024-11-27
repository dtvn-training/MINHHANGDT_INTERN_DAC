"""NOT COMPLETE YET"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import requests
import pandas as pd
from process.logics.ios_data_collector import IosDataCollector

class TestIosDataCollector(unittest.TestCase):

    @patch('logics.collectors.ios_data_collector.requests.get')
    @patch('logics.collectors.ios_data_collector.BeautifulSoup')
    def test_collect_ios_data(self, mock_beautiful_soup, mock_requests_get):
        # Arrange

        # Mock response from requests.get with a simple HTML structure
        mock_html_content = '''
        <html>
            <body>
                <div class="app-details">
                    <span class="app-description">Test description</span>
                    <span class="app-description">Test description 2</span>
                    <span class="app-description">Test description 3</span>
                </div>
                <div class="category-provider">
                    <span class="category">Test category</span>
                    <span class="provider">Test provider</span>
                    <span class="price">Free</span>
                </div>
            </body>
        </html>
        '''
        mock_response = MagicMock()
        mock_response.text = mock_html_content
        mock_requests_get.return_value = mock_response

        # Mock BeautifulSoup behavior
        mock_soup = MagicMock()
        mock_beautiful_soup.return_value = mock_soup

        # Mocking find_all to return a list with at least 2 elements
        mock_section1 = MagicMock()
        mock_section2 = MagicMock()
        mock_section3 = MagicMock()

        mock_soup.find_all.return_value = [mock_section1, mock_section2]  # Make sure there are at least 2 items

        mock_section1.find.return_value.get_text.return_value = 'Test description'
        mock_section2.find.return_value.get_text.return_value = 'Test description 2'

        # Mock category and provider information
        mock_category_section = MagicMock()
        mock_soup.find_all.return_value = [mock_category_section]
        mock_category_section.find.return_value.get_text.return_value = 'Test category'

        mock_category_section.find_all.return_value = [
            MagicMock(get_text=MagicMock(return_value='Test category')),
            MagicMock(get_text=MagicMock(return_value='Test provider')),
            MagicMock(get_text=MagicMock(return_value='Free'))
        ]

        # Create a mock DataFrame
        data = {'title': ['Test App'], 'link': ['http://testapp.com'], 'subtitle': ['Test Subtitle'], 'img_links': [['http://img1.com']]}
        df_mock = pd.DataFrame(data)

        collector = IosDataCollector()

        # Act
        collector.collect_ios_data(df_mock)

        # Assert
        collected_apps = collector.get_collected_ios_apps()
        self.assertEqual(len(collected_apps), 1)
        self.assertEqual(collected_apps[0].app_name, 'Test App')
        self.assertEqual(collected_apps[0].category, 'Test category')
        self.assertEqual(collected_apps[0].provider, 'Test provider')
        self.assertEqual(collected_apps[0].price, 0)  # Price is 'Free'

if __name__ == '__main__':
    unittest.main()
