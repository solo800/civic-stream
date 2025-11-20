import requests
import json
import logging
import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegistarScraper:
    """Scraper for Legistar API (works with any city)"""
    
    def __init__(self, city: str, api_token: Optional[str] = None):
        self.city = city
        self.base_url = f"https://webapi.legistar.com/v1/{city}"
        
        # Load city configuration
        self.city_config = self._load_city_config(city)
        
        # Try to load API token from various sources
        self.api_token = api_token or self._load_city_token(city)
        
        # Check if token is required but not available
        token_required = self.city_config.get('token_required', False)
        if token_required and not self.api_token:
            raise ValueError(f"API token is required for {city} but none was provided. "
                           f"Set LEGISTAR_{city.upper()}_TOKEN environment variable or "
                           f"add token to city_scraper.json")
        
        # Log token status
        if self.api_token:
            logger.info(f"Using API token for {city} (token: {self.api_token[:8]}...)")
        else:
            logger.info(f"No API token available for {city} - using public access")
        
        self.session = requests.Session()
        # Set a user agent to be polite
        self.session.headers.update({
            'User-Agent': 'civic-stream/1.0 (https://github.com/your-org/civic-stream)'
        })
    
    def _load_city_config(self, city: str) -> Dict[str, Any]:
        """Load city configuration from city_scraper.json file"""
        keys_file = Path(__file__).parent / "city_scraper.json"
        logger.debug(f"Looking for city config file at: {keys_file}")
        
        try:
            if keys_file.exists():
                logger.debug(f"Found city config file: {keys_file}")
                with open(keys_file, 'r', encoding='utf-8') as f:
                    city_configs = json.load(f)
                    config = city_configs.get(city, {})
                    if config:
                        logger.debug(f"Loaded configuration for {city}")
                        return config
                    else:
                        logger.debug(f"No configuration found for city '{city}' in city_scraper.json")
            else:
                logger.debug(f"City config file does not exist: {keys_file}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in city_scraper.json: {e}")
            logger.error("Please check the file for syntax errors or invalid characters")
        except Exception as e:
            logger.warning(f"Could not load city config from file: {e}")
        
        return {}

    def _load_city_token(self, city: str) -> Optional[str]:
        """Load API token for city from environment or config file"""
        # First try environment variable specific to the city
        env_token = os.getenv(f'LEGISTAR_{city.upper()}_TOKEN')
        if env_token:
            logger.info(f"Loaded API token for {city} from environment variable LEGISTAR_{city.upper()}_TOKEN")
            return env_token
        
        # Then try the config file
        config = self._load_city_config(city)
        token = config.get('token')
        if token:
            logger.info(f"Loaded API token for {city} from city_scraper.json")
            return token
        
        return None
    
    def _add_token_to_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add API token to request parameters if available"""
        if self.api_token:
            params['token'] = self.api_token
            logger.debug(f"Added API token to request parameters")
        else:
            logger.debug("No API token available - making unauthenticated request")
        return params
    
    def fetch_recent_matters(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch recent matters from Legistar API
        
        Args:
            limit: Number of matters to fetch (default 5)
            
        Returns:
            List of matter dictionaries
        """
        url = f"{self.base_url}/matters"
        params = {
            '$top': limit,
            '$orderby': 'MatterIntroDate desc'
        }
        params = self._add_token_to_params(params)
        
        try:
            logger.info(f"Fetching {limit} recent matters from {self.city} Legistar API")
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            matters = response.json()
            logger.info(f"Successfully fetched {len(matters)} matters")
            
            return matters
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching matters: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            raise
    
    def extract_matter_info(self, matter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant information from a matter record
        
        Args:
            matter: Raw matter dictionary from API
            
        Returns:
            Cleaned matter information
        """
        return {
            'id': matter.get('MatterId'),
            'file_number': matter.get('MatterFile'),
            'name': matter.get('MatterName'),
            'title': matter.get('MatterTitle'),
            'type': matter.get('MatterTypeName'),
            'status': matter.get('MatterStatusName'),
            'intro_date': matter.get('MatterIntroDate'),
            'agenda_date': matter.get('MatterAgendaDate'),
            'passed_date': matter.get('MatterPassedDate'),
            'enactment_date': matter.get('MatterEnactmentDate'),
            'enactment_number': matter.get('MatterEnactmentNumber'),
            'requester': matter.get('MatterRequester'),
            'notes': matter.get('MatterNotes'),
            'version': matter.get('MatterVersion'),
            'text1': matter.get('MatterText1'),
            'text2': matter.get('MatterText2'),
            'text3': matter.get('MatterText3'),
            'text4': matter.get('MatterText4'),
            'text5': matter.get('MatterText5'),
            'date_scraped': datetime.utcnow().isoformat(),
            'source_url': f"https://webapi.legistar.com/v1/{self.city}/matters/{matter.get('MatterId')}"
        }
    
    def scrape_and_process(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Main method to scrape and process matters
        
        Args:
            limit: Number of matters to fetch
            
        Returns:
            List of processed matter information
        """
        raw_matters = self.fetch_recent_matters(limit)
        processed_matters = []
        
        for matter in raw_matters:
            try:
                processed_matter = self.extract_matter_info(matter)
                processed_matters.append(processed_matter)
                logger.info(f"Processed matter: {processed_matter.get('file_number')} - {processed_matter.get('name')}")
            except Exception as e:
                logger.error(f"Error processing matter {matter.get('MatterId', 'unknown')}: {e}")
                continue
        
        return processed_matters
    
    def save_to_json(self, matters: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Save matters to JSON file
        
        Args:
            matters: List of processed matters
            filename: Output filename (optional)
            
        Returns:
            Filename of saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.city}_matters_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(matters, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Saved {len(matters)} matters to {filename}")
        return filename

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Scrape Legistar API for legislative matters')
    parser.add_argument('city', 
                       help='City code for Legistar API (e.g., "nyc", "chicago", "seattle")')
    parser.add_argument('--token', '-t', 
                       help='API token for Legistar API (can also use LEGISTAR_API_TOKEN env var)')
    parser.add_argument('--limit', '-l', type=int, default=5,
                       help='Number of matters to fetch (default: 5)')
    parser.add_argument('--output', '-o',
                       help='Output filename (default: auto-generated with timestamp)')
    
    args = parser.parse_args()
    
    # Get API token from command line argument or environment variable
    api_token = args.token or os.getenv('LEGISTAR_API_TOKEN')
    
    if api_token:
        logger.info("Using API token for authentication")
    else:
        logger.warning("No API token provided - some endpoints may be limited")
        logger.info("Use --token <token> or set LEGISTAR_API_TOKEN environment variable")
    
    scraper = LegistarScraper(city=args.city, api_token=api_token)
    
    try:
        # Scrape recent matters
        matters = scraper.scrape_and_process(limit=args.limit)
        
        # Save to JSON file
        filename = scraper.save_to_json(matters, args.output)
        
        # Print summary
        print(f"\nScraping completed successfully!")
        print(f"Fetched {len(matters)} matters from {args.city}")
        print(f"Saved to: {filename}")
        
        # Print brief summary of each matter
        print(f"\nRecent matters from {args.city}:")
        for matter in matters:
            print(f"- {matter['file_number']}: {matter['name']}")
            print(f"  Type: {matter['type']}, Status: {matter['status']}")
            print(f"  Intro Date: {matter['intro_date']}")
            print()
            
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise

if __name__ == "__main__":
    main()
