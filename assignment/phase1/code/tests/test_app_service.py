import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'code')))

import unittest
from unittest.mock import MagicMock, patch
from process.logics.app_service import AppService
from process.models.android_app import AndroidApp
from process.models.ios_app import IosApp

class TestAppService(unittest.TestCase):

    @patch('process.logics.app_service.SessionLocal')
    def test_insert_app_success(self, MockSessionLocal):

        #Arrange
        mock_session = MagicMock()
        MockSessionLocal.return_value = mock_session
        app_service = AppService()
        mock_app = MagicMock()

        #Act
        app_service.insert_app(mock_app)

        #Assert
        mock_session.add.assert_called_once_with(mock_app)
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    @patch('process.logics.app_service.SessionLocal')
    def test_insert_app_failure(self, MockSessionLocal):

        #Arrange
        mock_session = MagicMock()
        MockSessionLocal.return_value = mock_session
        app_service = AppService()
        mock_app = MagicMock()

        #Simulate an exception during commit
        mock_session.commit.side_effect = Exception("Database error")

        #Act
        app_service.insert_app(mock_app)

        #Assert
        mock_session.add.assert_called_once_with(mock_app)
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    @patch('process.logics.app_service.SessionLocal')
    def test_get_app_by_id_android(self, MockSessionLocal):
        #Arrange
        mock_session = MagicMock()
        MockSessionLocal.return_value = mock_session
        app_service = AppService()
        
        # Initialize mock_app with AndroidApp properties
        mock_app = MagicMock(spec=AndroidApp)
        mock_app.app_id = '1'
        mock_app.app_name = 'Mock Android App'
        mock_app.category = 'Games'
        mock_app.price = 0.99
        mock_app.provider = 'MockProvider'
        mock_app.description = 'This is a mock app.'
        mock_app.developer_email = 'developer@mock.com'
        
        # Simulate the results returned when calling the query
        mock_session.query.return_value.filter.return_value.first.return_value = mock_app

        # Act: Call the method to be tested
        result = app_service.get_app_by_id('1', 'android')

        # Assert: Check the result
        mock_session.query.return_value.filter.assert_called_once()
        args = mock_session.query.return_value.filter.call_args[0]
        
        # Check that the value '1' appears in the parameters
        self.assertIn('1', str(args[0]))  # Instead of checking for exact, check for '1' in parameter

        # Check the returned result is mock_app
        self.assertEqual(result, mock_app)

    @patch('process.logics.app_service.SessionLocal')
    def test_get_app_by_id_ios(self, MockSessionLocal):
        # Arrange: Set up mock session and necessary objects
        mock_session = MagicMock()
        MockSessionLocal.return_value = mock_session
        app_service = AppService()

        # Initialize mock_app with Ios App properties
        mock_app = MagicMock(spec=IosApp)
        mock_app.app_id = '1'
        mock_app.app_name = 'Mock iOS App'
        mock_app.category = 'Productivity'
        mock_app.price = 1.99
        mock_app.provider = 'MockProvider'
        mock_app.description = 'This is a mock iOS app.'
        mock_app.score = 4.5
        mock_app.cnt_rates = 1000
        mock_app.subtitle = 'Mock subtitle'
        mock_app.link = 'https://mock.com'
        mock_app.img_links = 'https://mock.com/img.png'

        # Simulate the results returned when calling the query
        mock_session.query.return_value.filter.return_value.first.return_value = mock_app

        # Act: Call the method to be tested
        result = app_service.get_app_by_id(1, 'ios')

        # Assert: Check the results
        mock_session.query.return_value.filter.assert_called_once()
        args = mock_session.query.return_value.filter.call_args[0]
        
        # Check that the value '1' appears in the parameters
        self.assertIn('1', str(args[0]))  # Check if '1' is in parameter

        # Check the returned result is mock_app
        self.assertEqual(result, mock_app)

if __name__ == "__main__":
    unittest.main()
