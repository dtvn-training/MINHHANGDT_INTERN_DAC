"""NOT COMPLETE YET"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'code')))

import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import requests
import pandas as pd
from process.logics.ios_data_collector import IosDataCollector
from process.models.ios_app import IosApp

class TestIosDataCollector(unittest.TestCase):
    
    @patch('process.logics.ios_data_collector.requests.get')
    @patch('process.logics.ios_data_collector.BeautifulSoup')
    @patch('process.logics.ios_data_collector.IosApp')
    def test_collect_ios_data(self, mock_ios_app, mock_bs4, mock_requests_get):
        # Mock HTML response from requests.get
        mock_html = """
        <html>
            <section class="l-content-width section section--bordered"></section>

            <section class="l-content-width section section--bordered">
                <p>Description of the app.</p>
            </section>

            <section class="l-content-width section section--bordered">
                <div class="we-customer-ratings lockup">
                    <div class="we-customer-ratings__stats l-column small-4 medium-6 large-4">
                        <div class="we-customer-ratings__averages">
                            <span>4.5</span>
                        </div>
                        <div class="we-customer-ratings__count small-hide medium-show">
                            1234 ratings
                        </div>
                    </div>
                </div>
            </section>

            <section class="l-content-width section section--bordered section--information">
                <div class="information-list__item l-column small-12 medium-6 large-4 small-valign-top">
                    <dd class="information-list__item__definition">100 MB</dd>
                </div>
                <dl class="information-list information-list--app medium-columns l-row">
                    <dd class="information-list__item__definition">Provider XYZ</dd>
                    <dd class="information-list__item__definition"></dd>
                    <dd class="information-list__item__definition">Games</dd>
                    <dd class="information-list__item__definition"></dd>
                    <dd class="information-list__item__definition"></dd>
                    <dd class="information-list__item__definition"></dd>
                    <dd class="information-list__item__definition"></dd>
                    <dd class="information-list__item__definition">Free</dd>
                </dl>
            </section>

        </html>
        """
        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_requests_get.return_value = mock_response

        # Mock BeautifulSoup to return sections correctly
        mock_soup = BeautifulSoup(mock_html, 'html.parser')
        mock_bs4.return_value = mock_soup

        # Mock IosApp creation
        mock_ios_app.return_value = MagicMock()

        # Create a mock DataFrame df_ids
        df_ids = pd.DataFrame({
            'rank': [1],
            'title': ['Test App'],
            'subtitle': ['Test Subtitle'],
            'link': ['http://example.com'],
            'img_links': [['http://example.com/image1.jpg', 'http://example.com/image2.jpg']]
        })

        # Create an instance of IosDataCollector
        collector = IosDataCollector()

        # Run the method to collect data
        collector.collect_ios_data(df_ids)

        # Assert that the HTTP request was made to the correct URL
        mock_requests_get.assert_called_once_with('http://example.com', allow_redirects=False)

        # Assert that IosApp was called with correct parameters
        mock_ios_app.assert_called_once_with(
            app_id='Test App',
            app_name='Test App',
            category='Games',
            price=0,
            provider='Provider XYZ',
            description='Description of the app.',
            score=4.5,
            cnt_rates=1234,
            subtitle='Test Subtitle',
            link='http://example.com',
            img_links='http://example.com/image1.jpg,http://example.com/image2.jpg'
        )

        # Assert that the ios_apps list has one item
        self.assertEqual(len(collector.ios_apps), 1)

        # Verify that the collected app is an instance of IosApp
        self.assertIsInstance(collector.ios_apps[0], MagicMock)


if __name__ == '__main__':
    unittest.main()
