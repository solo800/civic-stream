# civic-stream

## Overview
civic-stream allows users to subscribe to public city communications (press releases, public notices, agendas, meeting minutes, budget documents, planning announcements, etc.) and receive AI-generated summaries with action links to email city officials or share opinions on social media.

## Current State
**Early-stage MVP** - Basic project structure is in place with working scraper implementation.

The project currently includes:
- ✅ Multi-city Legistar API scraper with comprehensive test suite
- ✅ Token-based authentication system with fallback support
- ✅ Environment variable and JSON configuration file management
- ✅ Automated results directory structure with timestamped outputs
- ✅ Robust error handling and logging throughout
- ✅ City-specific configuration with token requirement validation
- ✅ Python dependency management (requirements.txt)
- ✅ Comprehensive documentation and project scaffolding

We're starting with Legistar APIs across multiple cities to validate the concept before expanding to other content types. The scraper currently supports 5 cities with configurable authentication requirements and produces structured JSON output for downstream processing.

## Architecture

### High-Level Flow
1. **Scraper (Fargate)** runs on schedule → fetches new city documents → stores in S3
2. **Summarize Lambda** triggered by S3 → calls Claude API → stores summary in DynamoDB
3. **Notify Lambda** → emails subscribers via SES with summary + action links
4. **API (Lambda + API Gateway)** handles user signup, subscriptions, and data retrieval
5. **Frontend (S3 + CloudFront)** static React site for browsing and managing subscriptions

### Components

**Frontend**
- Static React site
- Hosted on S3 + CloudFront
- Mobile-first responsive design
- Eventually: native mobile app

**Scraper**
- Python + Selenium in Docker container
- Runs on AWS Fargate (ECS scheduled tasks)
- Handles various document formats (PDFs, HTML, embedded viewers)
- Flexible to support different city website structures

**Lambda Functions**
- **Summarize**: Processes documents using Claude API
- **Notify**: Sends email summaries to subscribers via SES
- **API**: User management, subscription CRUD operations

**Data Storage**
- **S3**: Raw documents from cities
- **DynamoDB**: Users, subscriptions, document metadata, summaries

## Tech Stack
- **Languages**: Python (backend/scrapers), JavaScript/React (frontend)
- **AWS Services**: Fargate, Lambda, S3, CloudFront, DynamoDB, SES, API Gateway, EventBridge
- **AI**: Claude API (Anthropic)
- **Scraping**: Selenium + headless Chrome

## Project Structure
```
civic-stream/
├── scraper/              # Fargate container for scraping city sites
│   ├── legistar_scraper.py      # Main scraper implementation
│   ├── test_legistar_scraper.py # Comprehensive test suite
│   ├── city_scraper.json        # City configuration and tokens
│   └── results/                 # Output directory (gitignored)
│       └── .gitkeep
├── functions/            # Lambda functions
│   ├── summarize/       # Claude API summarization
│   ├── notify/          # Email notifications
│   └── api/             # API Gateway handlers
├── frontend/            # Static React site
│   ├── public/
│   └── src/
├── requirements.txt     # Python dependencies
├── .aider.conf.yml      # Aider configuration (Claude 4 Sonnet)
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd civic-stream
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Scraper

#### Prerequisites for NYC
NYC requires an API token. You can provide it in three ways:

1. **Environment variable** (recommended):
   ```bash
   export LEGISTAR_NYC_TOKEN="your_token_here"
   cd scraper
   python legistar_scraper.py nyc --limit 3
   ```

2. **Command line argument**:
   ```bash
   cd scraper
   python legistar_scraper.py nyc --token "your_token_here" --limit 3
   ```

3. **Configuration file**: Add your token to `scraper/city_scraper.json` (already configured)

#### Test other cities (no token required):
```bash
cd scraper
python legistar_scraper.py chicago --limit 3
python legistar_scraper.py seattle --limit 3
python legistar_scraper.py boston --limit 3
python legistar_scraper.py oakland --limit 3
```

#### Available command line options:
```bash
python legistar_scraper.py <city> [options]
  --limit, -l    Number of matters to fetch (default: 5)
  --token, -t    API token for authentication
  --output, -o   Custom output filename
```

#### Run the test suite:
```bash
cd scraper
python -m pytest test_legistar_scraper.py -v
```

#### Output
All scraped data is automatically saved to `scraper/results/` directory with timestamped filenames like `nyc_matters_20231120_143022.json`. Each output file contains structured JSON with:
- Matter metadata (ID, file number, title, type, status)
- Important dates (intro, agenda, passed, enactment)
- Full text content and notes
- Scraping timestamp and source URL

### Dependencies
Core dependencies are managed in `requirements.txt`:
- `requests` - HTTP client for API calls
- `pytest` - Testing framework
- `black` - Code formatting
- `flake8` - Code linting

### Configuration
The scraper supports multiple cities through `scraper/city_scraper.json`:
- **Token management**: Store API tokens securely (base64 encoded)
- **Token requirements**: Automatic validation prevents API calls without required tokens
- **City descriptions**: Human-readable city names for documentation
- **Flexible authentication**: Environment variables override config file settings

Supported cities:
- **NYC** (token required): New York City Council - Full legislative data access
- **Chicago** (public): Chicago City Council - Public API access
- **Seattle** (public): Seattle City Council - Public API access  
- **Boston** (public): Boston City Council - Public API access
- **Oakland** (public): Oakland City Council - Public API access

The scraper automatically detects token requirements and will fail fast with clear error messages if authentication is needed but not provided.

## Development Notes

### Why Fargate instead of Lambda for scraping?
Lambda has 15-minute execution limits and limited support for browser automation. Many city websites use PDF viewers or JavaScript-heavy interfaces that require Selenium with an actual browser. Fargate gives us:
- No time limits
- Full browser automation support
- Easier local development (Docker)

### AWS Setup
Currently using manual AWS console setup. Will consider IaC (CDK/Terraform) once architecture stabilizes.

### Content Strategy
Starting broad with any public city communications rather than just meeting minutes:
- Press releases (often have RSS feeds - easier to start with)
- Public notices
- Agendas (published before meetings - more timely)
- Meeting minutes (when ready)
- Planning/zoning announcements
- Budget documents

This makes the product more immediately useful and tests different scraping patterns.

## Next Steps
- [x] Choose target city with accessible content (NYC Legistar API)
- [x] Build basic scraper for one content type (legislative matters)
- [x] Add dependency management (requirements.txt)
- [x] Create comprehensive test suite
- [x] Multi-city configuration system with 5 supported cities
- [x] Token management and authentication with environment variable support
- [x] Results directory structure with organized JSON output
- [x] Robust error handling and logging system
- [x] Command-line interface with flexible options
- [ ] Set up DynamoDB schema for storing scraped data
- [ ] Create summarization Lambda using Claude API
- [ ] Build simple frontend for email signup and city selection
- [ ] Implement notification system with SES integration
- [ ] Test end-to-end flow with one city (NYC ready for integration)
- [ ] Add Docker containerization for Fargate deployment
- [ ] Implement incremental scraping (only fetch new/updated matters)
- [ ] Add support for additional Legistar endpoints (votes, people, events)

## Future Considerations
- Multi-city support
- User preference management (notification frequency, topics of interest)
- Social media integration (pre-populated posts)
- Email template system for contacting officials
- Analytics/engagement tracking
- Mobile app (React Native)
