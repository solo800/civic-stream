# Legistar Scraper

A generic scraper for Legistar APIs that works with any city using the Legistar system.

## Setup

1. Create a `city_keys.json` file in this directory with your API tokens:
```json
{
  "nyc": "your_nyc_token_here",
  "oakland": "your_oakland_token_here",
  "chicago": ""
}
```

2. The `city_keys.json` file is automatically ignored by git for security.

## Manual Testing

### Basic Usage

Test with NYC (3 matters):
Note that my alias for py3 is py.
```bash
py legistar_scraper.py nyc --limit 3
```

Test with Oakland (5 matters):
```bash
py legistar_scraper.py oakland --limit 5
```

Test with a custom output file:
```bash
py legistar_scraper.py nyc --limit 10 --output nyc_test.json
```

### Using API Tokens

The scraper will automatically load tokens from `city_keys.json`. You can also:

Use environment variable:
```bash
export LEGISTAR_API_TOKEN="your_token_here"
py legistar_scraper.py nyc --limit 3
```

Use command line argument:
```bash
py legistar_scraper.py nyc --token "your_token_here" --limit 3
```

### Checking Results

View the generated JSON file:
```bash
cat nyc_matters_*.json | jq '.[0]'  # View first matter (requires jq)
```

List all generated files:
```bash
ls -la *_matters_*.json
```

### Testing Different Cities

Common city codes to test:
- `nyc` - New York City
- `oakland` - Oakland, CA
- `chicago` - Chicago, IL
- `seattle` - Seattle, WA
- `boston` - Boston, MA

Example test sequence:
```bash
# Test NYC
py legistar_scraper.py nyc --limit 2

# Test Oakland  
py legistar_scraper.py oakland --limit 2

# Check what files were created
ls -la *_matters_*.json

# View a sample record
head -50 nyc_matters_*.json
```

### Troubleshooting

If you get a 403 error:
- Make sure your API token is correct in `city_keys.json`
- Some cities may require tokens for all endpoints
- Check that the city code is correct

If you get a 404 error:
- The city may not use Legistar or may use a different city code
- Try checking the Legistar documentation for the correct city identifier

### Expected Output

Successful runs will show:
- Log messages about fetching matters
- A summary of processed matters
- File location of saved JSON data
- Brief details of each matter (file number, name, type, status, intro date)

The JSON output contains structured data with fields like:
- `id`, `file_number`, `name`, `title`
- `type`, `status`, `intro_date`
- `requester`, `notes`, `enactment_number`
- `date_scraped`, `source_url`
