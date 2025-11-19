import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import os
import tempfile
from datetime import datetime
import requests

from legistar_scraper import LegistarScraper


class TestLegistarScraper(unittest.TestCase):
    """Test cases for LegistarScraper class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scraper = LegistarScraper()
        self.scraper_with_token = LegistarScraper(api_token="test_token")
        
        # Sample matter data for testing
        self.sample_matter = {
            'MatterId': 12345,
            'MatterFile': 'Int 0123-2024',
            'MatterName': 'Test Matter',
            'MatterTitle': 'A Local Law to amend the administrative code',
            'MatterTypeName': 'Introduction',
            'MatterStatusName': 'Committee',
            'MatterIntroDate': '2024-01-15T00:00:00',
            'MatterAgendaDate': '2024-01-20T00:00:00',
            'MatterPassedDate': None,
            'MatterEnactmentDate': None,
            'MatterEnactmentNumber': None,
            'MatterRequester': 'Council Member Smith',
            'MatterNotes': 'Test notes',
            'MatterVersion': '1',
            'MatterText1': 'Summary text',
            'MatterText2': None,
            'MatterText3': None,
            'MatterText4': None,
            'MatterText5': None
        }
    
    def test_init_without_token(self):
        """Test initialization without API token"""
        scraper = LegistarScraper()
        self.assertEqual(scraper.base_url, "https://webapi.legistar.com/v1/nyc")
        self.assertIsNone(scraper.api_token)
        self.assertIsInstance(scraper.session, requests.Session)
    
    def test_init_with_token(self):
        """Test initialization with API token"""
        token = "test_token_123"
        scraper = LegistarScraper(api_token=token)
        self.assertEqual(scraper.api_token, token)
    
    def test_add_token_to_params_without_token(self):
        """Test _add_token_to_params when no token is set"""
        params = {'key': 'value'}
        result = self.scraper._add_token_to_params(params)
        self.assertEqual(result, {'key': 'value'})
    
    def test_add_token_to_params_with_token(self):
        """Test _add_token_to_params when token is set"""
        params = {'key': 'value'}
        result = self.scraper_with_token._add_token_to_params(params)
        expected = {'key': 'value', 'token': 'test_token'}
        self.assertEqual(result, expected)
    
    @patch('legistar_scraper.requests.Session.get')
    def test_fetch_recent_matters_success(self, mock_get):
        """Test successful fetch of recent matters"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = [self.sample_matter]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch_recent_matters(limit=1)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.sample_matter)
        
        # Verify the API call was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn('matters', call_args[0][0])  # URL contains 'matters'
        self.assertEqual(call_args[1]['params']['$top'], 1)
        self.assertEqual(call_args[1]['params']['$orderby'], 'MatterIntroDate desc')
    
    @patch('legistar_scraper.requests.Session.get')
    def test_fetch_recent_matters_with_token(self, mock_get):
        """Test fetch with API token"""
        mock_response = Mock()
        mock_response.json.return_value = [self.sample_matter]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        self.scraper_with_token.fetch_recent_matters(limit=1)
        
        # Verify token was added to params
        call_args = mock_get.call_args
        self.assertEqual(call_args[1]['params']['token'], 'test_token')
    
    @patch('legistar_scraper.requests.Session.get')
    def test_fetch_recent_matters_request_exception(self, mock_get):
        """Test handling of request exceptions"""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        with self.assertRaises(requests.exceptions.RequestException):
            self.scraper.fetch_recent_matters()
    
    @patch('legistar_scraper.requests.Session.get')
    def test_fetch_recent_matters_json_decode_error(self, mock_get):
        """Test handling of JSON decode errors"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_get.return_value = mock_response
        
        with self.assertRaises(json.JSONDecodeError):
            self.scraper.fetch_recent_matters()
    
    def test_extract_matter_info(self):
        """Test extraction of matter information"""
        with patch('legistar_scraper.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value.isoformat.return_value = "2024-01-01T12:00:00"
            
            result = self.scraper.extract_matter_info(self.sample_matter)
            
            expected = {
                'id': 12345,
                'file_number': 'Int 0123-2024',
                'name': 'Test Matter',
                'title': 'A Local Law to amend the administrative code',
                'type': 'Introduction',
                'status': 'Committee',
                'intro_date': '2024-01-15T00:00:00',
                'agenda_date': '2024-01-20T00:00:00',
                'passed_date': None,
                'enactment_date': None,
                'enactment_number': None,
                'requester': 'Council Member Smith',
                'notes': 'Test notes',
                'version': '1',
                'text1': 'Summary text',
                'text2': None,
                'text3': None,
                'text4': None,
                'text5': None,
                'date_scraped': "2024-01-01T12:00:00",
                'source_url': "https://webapi.legistar.com/v1/nyc/matters/12345"
            }
            
            self.assertEqual(result, expected)
    
    def test_extract_matter_info_missing_fields(self):
        """Test extraction with missing fields"""
        incomplete_matter = {'MatterId': 999}
        
        with patch('legistar_scraper.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value.isoformat.return_value = "2024-01-01T12:00:00"
            
            result = self.scraper.extract_matter_info(incomplete_matter)
            
            # Should handle missing fields gracefully
            self.assertEqual(result['id'], 999)
            self.assertIsNone(result['file_number'])
            self.assertIsNone(result['name'])
            self.assertEqual(result['date_scraped'], "2024-01-01T12:00:00")
    
    @patch.object(LegistarScraper, 'fetch_recent_matters')
    def test_scrape_and_process_success(self, mock_fetch):
        """Test successful scrape and process"""
        mock_fetch.return_value = [self.sample_matter]
        
        with patch('legistar_scraper.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value.isoformat.return_value = "2024-01-01T12:00:00"
            
            result = self.scraper.scrape_and_process(limit=1)
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['id'], 12345)
            self.assertEqual(result[0]['file_number'], 'Int 0123-2024')
    
    @patch.object(LegistarScraper, 'fetch_recent_matters')
    def test_scrape_and_process_with_error(self, mock_fetch):
        """Test scrape and process with processing error"""
        # Create a matter that will cause an error in extract_matter_info
        bad_matter = {'MatterId': 'invalid'}
        mock_fetch.return_value = [self.sample_matter, bad_matter]
        
        with patch.object(self.scraper, 'extract_matter_info') as mock_extract:
            mock_extract.side_effect = [
                {'id': 12345, 'file_number': 'Int 0123-2024'},  # First call succeeds
                Exception("Processing error")  # Second call fails
            ]
            
            result = self.scraper.scrape_and_process(limit=2)
            
            # Should return only the successfully processed matter
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['id'], 12345)
    
    def test_save_to_json_with_filename(self):
        """Test saving to JSON with specified filename"""
        matters = [{'id': 1, 'name': 'Test'}]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_file:
            filename = tmp_file.name
        
        try:
            result_filename = self.scraper.save_to_json(matters, filename)
            self.assertEqual(result_filename, filename)
            
            # Verify file contents
            with open(filename, 'r') as f:
                saved_data = json.load(f)
            
            self.assertEqual(saved_data, matters)
        finally:
            os.unlink(filename)
    
    def test_save_to_json_auto_filename(self):
        """Test saving to JSON with auto-generated filename"""
        matters = [{'id': 1, 'name': 'Test'}]
        
        with patch('legistar_scraper.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
            
            filename = self.scraper.save_to_json(matters)
            
            expected_filename = "nyc_matters_20240101_120000.json"
            self.assertEqual(filename, expected_filename)
            
            # Clean up
            if os.path.exists(filename):
                os.unlink(filename)


class TestMainFunction(unittest.TestCase):
    """Test cases for main function"""
    
    @patch('legistar_scraper.LegistarScraper')
    @patch('legistar_scraper.argparse.ArgumentParser.parse_args')
    def test_main_with_token_argument(self, mock_parse_args, mock_scraper_class):
        """Test main function with token argument"""
        # Mock command line arguments
        mock_args = Mock()
        mock_args.token = "test_token"
        mock_args.limit = 5
        mock_args.output = None
        mock_parse_args.return_value = mock_args
        
        # Mock scraper instance
        mock_scraper = Mock()
        mock_scraper.scrape_and_process.return_value = [{'id': 1, 'file_number': 'Test'}]
        mock_scraper.save_to_json.return_value = "test_output.json"
        mock_scraper_class.return_value = mock_scraper
        
        # Import and run main (need to import here to avoid issues with patches)
        from legistar_scraper import main
        
        with patch('builtins.print'):  # Suppress print output
            main()
        
        # Verify scraper was initialized with token
        mock_scraper_class.assert_called_once_with(api_token="test_token")
        mock_scraper.scrape_and_process.assert_called_once_with(limit=5)
    
    @patch('legistar_scraper.LegistarScraper')
    @patch('legistar_scraper.argparse.ArgumentParser.parse_args')
    @patch.dict(os.environ, {'LEGISTAR_API_TOKEN': 'env_token'})
    def test_main_with_env_token(self, mock_parse_args, mock_scraper_class):
        """Test main function with environment variable token"""
        mock_args = Mock()
        mock_args.token = None
        mock_args.limit = 3
        mock_args.output = "custom_output.json"
        mock_parse_args.return_value = mock_args
        
        mock_scraper = Mock()
        mock_scraper.scrape_and_process.return_value = []
        mock_scraper.save_to_json.return_value = "custom_output.json"
        mock_scraper_class.return_value = mock_scraper
        
        from legistar_scraper import main
        
        with patch('builtins.print'):
            main()
        
        # Verify scraper was initialized with environment token
        mock_scraper_class.assert_called_once_with(api_token="env_token")
        mock_scraper.save_to_json.assert_called_once_with([], "custom_output.json")


if __name__ == '__main__':
    unittest.main()
