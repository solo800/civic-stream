import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegistarScraper:
    """Scraper for San Francisco Legistar API"""
    
    def __init__(self):
        self.base_url = "https://webapi.legistar.com/v1/sanfrancisco"
        self.session = requests.Session()
        # Set a user agent to be polite
        self.session.headers.update({
            'User-Agent': 'civic-stream/1.0 (https://github.com/your-org/civic-stream)'
        })
    
    def fetch_recent_matters(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch recent matters from San Francisco Legistar API
        
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
        
        try:
            logger.info(f"Fetching {limit} recent matters from Legistar API")
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
            'source_url': f"https://webapi.legistar.com/v1/sanfrancisco/matters/{matter.get('MatterId')}"
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
            filename = f"sf_matters_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(matters, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Saved {len(matters)} matters to {filename}")
        return filename

def main():
    """Main execution function"""
    scraper = LegistarScraper()
    
    try:
        # Scrape recent matters
        matters = scraper.scrape_and_process(limit=5)
        
        # Save to JSON file
        filename = scraper.save_to_json(matters)
        
        # Print summary
        print(f"\nScraping completed successfully!")
        print(f"Fetched {len(matters)} matters")
        print(f"Saved to: {filename}")
        
        # Print brief summary of each matter
        print("\nRecent matters:")
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
