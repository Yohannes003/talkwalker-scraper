# Talkwalker Scraper

This project automates the process of logging into Talkwalker, saving cookies, and scraping data from the Talkwalker platform. The project includes three main scripts:

1. `talkwalker cookies.py`: Logs into Talkwalker and saves cookies.
2. `scraper.py`: Uses the saved cookies to scrape data from Talkwalker.
3. `scheduler.py`: Schedules the execution of the above scripts.

## Requirements

To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

## Files

### `talkwalker cookies.py`

This script logs into Talkwalker and saves the cookies to a file.

- **Username and Password**: Update the `username` and `password` variables with your Talkwalker credentials.
- **Wait for Page Load**: The script waits for the login page to load before entering the credentials.

### `scraper.py`

This script uses the saved cookies to scrape data from Talkwalker.

- **Initialize Driver**: Sets up the Firefox WebDriver.
- **Load Cookies**: Loads cookies from the `talkwalk_cookies.pkl` file.
- **Scroll and Collect Divs**: Scrolls down the page to collect all `<div>` elements with class `top`.
- **Login and Navigate**: Logs in and navigates to the desired page.
- **Interact with Elements**: Interacts with various elements on the page.
- **Click Influencer Icon**: Clicks the influencer icon.
- **Collect Influencer Data**: Collects data from each `<tr>` element with class `css-1kidomb`.
- **Scrape Gender Data**: Scrapes gender-related information.
- **Process Divs**: Collects and processes each `<div>` with class `top` and adds influencer and gender data.
- **Read Keywords from File**: Reads keywords from a text file.

### `scheduler.py`

This script schedules the execution of the `talkwalker cookies.py` and `scraper.py` scripts.

- **Run Scraper**: Defines the scraping task to run both scripts.
- **Schedule Task**: Schedules the task to run every 7 days.
- **Keep Scheduler Running**: Keeps the scheduler running, checking for pending tasks every second.

## Usage

1. **Update Credentials**: Update the `username` and `password` variables in `talkwalker cookies.py` with your Talkwalker credentials.
2. **Run Scheduler**: Execute the `scheduler.py` script to start the scheduler.

```bash
python scheduler.py
```

## Additional Information

- **MongoDB**: The `scraper.py` script stores the scraped data in a MongoDB database. Ensure MongoDB is running and accessible.
- **Keywords File**: The `scraper.py` script reads keywords from a `keywords.txt` file. Ensure this file exists and contains the keywords to be processed.

## Troubleshooting

- **TimeoutException**: If you encounter a `TimeoutException`, increase the wait time in the `WebDriverWait` calls.
- **Element Not Found**: Ensure the XPath and CSS selectors used in the scripts match the current structure of the Talkwalker website.

- **MongoDB Connection Issues**: Verify the MongoDB connection settings and ensure the database is accessible. ##
- **Keywords File Issues**: Ensure the `keywords.txt` file exists and contains the correct keywords.
