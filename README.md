# Crypto Address Metadata Update

A Python tool that automatically identifies and tags cryptocurrency addresses by querying multiple sources including Etherscan, OKLink, Ethtective, and Bloxy. This tool helps in identifying and categorizing blockchain addresses, particularly those associated with exchanges.

## Features

- 🔄 Multi-source address tagging
- 🌐 Support for major blockchain explorers:
  - Etherscan
  - OKLink API
  - Ethtective
  - Bloxy
- 🤖 Automated web scraping with rotating IPs
- 📊 MongoDB integration for data storage
- ⏱️ Rate limiting and request management
- 🔄 Progress tracking with tqdm
- 🛡️ Error handling and retry mechanisms

## Prerequisites

Before running this script, ensure you have the following installed:

```bash
pip install selenium
pip install beautifulsoup4
pip install pymongo
pip install requests
pip install tqdm
```

You'll also need:
- MongoDB server running locally on default port (27017)
- Chrome WebDriver for Selenium
- OKLink API key
- Python 3.x

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd crypto-address-tagger
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
export ok_tag_api='your-oklink-api-key'
```

## Configuration

Create a MongoDB database named `crypto_forensics` with the following collections:
- `ethereum_metadata_update`
- `ethereum_metadata_update_result`

## Usage

Run the script:

```bash
python main.py
```

The script will:
1. Query addresses from the MongoDB database
2. Check each address against multiple sources
3. Store tagged addresses in the result collection
4. Handle untagged addresses through multiple fallback sources

## Data Sources

### 1. Etherscan
- Primary source for Ethereum addresses
- Scrapes contract labels and tags
- Includes rate limiting and user-agent rotation

### 2. OKLink API
- Secondary source for address verification
- Provides entity labels and exchange identification
- Requires API key for access

### 3. Ethtective
- Tertiary source for address verification
- Uses Selenium for dynamic content scraping
- Provides detailed exchange information

### 4. Bloxy
- Final fallback source
- Provides additional address metadata
- Includes name annotations and tags

## Database Schema

Each tagged address entry contains:
```json
{
    "address": "string",
    "name": "string",
    "tag": "exchange",
    "source": "string",
    "confidence": 80,
    "timestamp": integer
}
```

## Features in Detail

### IP Rotation
- Generates random IPs for request headers
- Helps avoid rate limiting
- Configurable number of IPs

### Request Management
- Implements exponential backoff
- Handles connection errors
- Includes request retries

### Data Processing
- Batch processing of addresses
- Progress tracking with tqdm
- Error handling and logging

## Error Handling

The script includes comprehensive error handling for:
- API failures
- Network issues
- Rate limiting
- Parsing errors
- Database connection issues

## Performance

- Processes addresses in batches of 5000
- Implements appropriate delays between requests
- Uses connection pooling for MongoDB

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Note on Rate Limits

Please be aware of rate limits for different services:
- OKLink: Refer to your API plan limits
- Etherscan: ~5 requests per second
- Ethtective: Manual delay of 15 seconds
- Bloxy: Standard web scraping delays
