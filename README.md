# Crypto Address Metadata Update

This Python script is designed to update metadata for cryptocurrency addresses stored in a MongoDB database using various APIs and web scraping techniques. The metadata includes attributes like name, tag, source, confidence level, and timestamp.

## Features

- **APIs and Web Scraping**: Utilizes APIs from services like OkLink, Etherscan, and Bloxy, as well as web scraping via Selenium for Ethtective.
- **Random IP Generation**: Generates random IP addresses to mimic different requests.
- **MongoDB Integration**: Connects to a MongoDB instance to fetch and update data.
- **Error Handling**: Includes error handling for API requests and unexpected errors.
- **Progress Tracking**: Uses tqdm for progress tracking during address processing.

## Components

### `main()` Function

The `main()` function orchestrates the process:
1. Connects to MongoDB and fetches addresses that need metadata updating.
2. Iterates over addresses, attempting to tag them using various services.
3. Updates MongoDB with tagged addresses and handles addresses that remain untagged.

### Functions

- **`connect_mongodb(collection_name)`**: Connects to MongoDB and sets up the collections.
- **`etherscan(target_collection, address)`**: Retrieves metadata using the Etherscan API.
- **`oklink(target_collection, addr_list, chain="eth")`**: Tags addresses using the OkLink API.
- **`scrape_ethtective(address, target_collection)`**: Scrapes metadata from Ethtective using Selenium.
- **`bloxy(address, target_collection)`**: Retrieves metadata using the Bloxy API.

### Libraries Used

- **Requests**: HTTP library for making API requests.
- **BeautifulSoup**: For parsing HTML content.
- **Selenium**: For web scraping dynamic content (used with Chrome WebDriver).
- **Pymongo**: MongoDB driver for Python.
- **tqdm**: Progress bar library for tracking iterations.

## Usage

1. **Environment Setup**: Ensure required Python libraries (`requests`, `bs4`, `selenium`, `pymongo`, `tqdm`) are installed.
2. **MongoDB**: Set up a MongoDB instance locally or remotely and configure the connection string.
3. **API Keys**: Set environment variables for `ok_tag_api` (OkLink API key).
4. **Execution**: Run the script (`python script_name.py`) to update metadata for cryptocurrency addresses.

## Notes

- Adjustments may be needed in sleep durations (`time.sleep()`) depending on API rate limits and web page load times.
- Error handling and retry mechanisms can be enhanced based on specific use cases and API behaviors.
