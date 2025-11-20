# civic-stream

## Overview
civic-stream allows users to subscribe to public city communications (press releases, public notices, agendas, meeting minutes, budget documents, planning announcements, etc.) and receive AI-generated summaries with action links to email city officials or share opinions on social media.

## Current State
**Early-stage MVP** - Basic project structure is in place with initial scraper implementation.

The project currently includes:
- ✅ NYC Legistar API scraper with comprehensive test suite
- ✅ Multi-city configuration system with token management
- ✅ Environment variable and JSON file token loading
- ✅ Results directory structure for organized output
- ✅ Python dependency management (requirements.txt)
- ✅ Project scaffolding and documentation

We're starting with NYC's Legistar API to validate the concept before expanding to other cities and content types. The scraper now supports multiple cities with configurable token requirements.

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
NYC requires an API token. You can provide it in two ways:

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

3. **Configuration file**: Add your token to `scraper/city_scraper.json`

#### Test other cities (no token required):
```bash
cd scraper
python legistar_scraper.py chicago --limit 3
python legistar_scraper.py seattle --limit 3
python legistar_scraper.py boston --limit 3
python legistar_scraper.py oakland --limit 3
```

#### Run the test suite:
```bash
cd scraper
python -m pytest test_legistar_scraper.py -v
```

#### Output
All scraped data is automatically saved to `scraper/results/` directory with timestamped filenames like `nyc_matters_20231120_143022.json`.

### Dependencies
Core dependencies are managed in `requirements.txt`:
- `requests` - HTTP client for API calls
- `pytest` - Testing framework
- `black` - Code formatting
- `flake8` - Code linting

### Configuration
The scraper supports multiple cities through `scraper/city_scraper.json`:
- **Token management**: Store API tokens securely
- **Token requirements**: Configure which cities require authentication
- **City descriptions**: Human-readable city names

Supported cities:
- **NYC** (token required): New York City Council
- **Chicago** (public): Chicago City Council  
- **Seattle** (public): Seattle City Council
- **Boston** (public): Boston City Council
- **Oakland** (public): Oakland City Council

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
- [x] Multi-city configuration system
- [x] Token management and authentication
- [x] Results directory structure
- [ ] Set up DynamoDB schema
- [ ] Create summarization Lambda
- [ ] Build simple frontend for email signup
- [ ] Implement notification system
- [ ] Test end-to-end flow with one city
- [ ] Add Docker containerization for Fargate deployment

## Future Considerations
- Multi-city support
- User preference management (notification frequency, topics of interest)
- Social media integration (pre-populated posts)
- Email template system for contacting officials
- Analytics/engagement tracking
- Mobile app (React Native)
