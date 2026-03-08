import logging
import feedparser
import requests
import yaml
import os
import time
from datetime import datetime

# Adjust sys.path or use relative imports if run as a module, but here we assume it's run from main.py or directly
import database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - CRAWLER - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yml')

def load_config():
    """Loads settings and feed list from config.yml."""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config.yml: {e}")
        return None

def fetch_feed(url, timeout, retries=2):
    """Fetches feed content using requests for strict timeout and retry control."""
    for attempt in range(retries + 1):
        try:
            # We use a standard User-Agent to avoid being blocked by some servers
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AI_News_Archive/1.0"}
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.content
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching {url} (Attempt {attempt+1}/{retries+1})")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error fetching {url}: {e} (Attempt {attempt+1}/{retries+1})")
        
        if attempt < retries:
            time.sleep(2) # brief pause before retry
            
    logger.error(f"Completely failed to fetch {url} after {retries + 1} attempts.")
    return None

def run_crawler():
    """Main crawler loop over all configured RSS feeds."""
    logger.info("Starting Web Crawler...")
    
    config = load_config()
    if not config or 'rss_feeds' not in config:
        logger.error("Invalid configuration. Aborting crawl.")
        return

    timeout = config.get('settings', {}).get('crawler', {}).get('timeout_seconds', 10)
    max_retries = config.get('settings', {}).get('crawler', {}).get('max_retries', 2)
    
    total_found = 0
    total_inserted = 0
    failed_feeds = 0

    # Iterate through Categories and their URLs
    for category, urls in config['rss_feeds'].items():
        logger.info(f"Processing category: {category}")
        
        for url in urls:
            logger.info(f" -> Fetching: {url}")
            feed_content = fetch_feed(url, timeout=timeout, retries=max_retries)
            
            if not feed_content:
                failed_feeds += 1
                continue
                
            # Parse the fetched XML using feedparser
            parsed_feed = feedparser.parse(feed_content)
            source_title = parsed_feed.feed.get('title', 'Unknown Source')
            
            for entry in parsed_feed.entries:
                total_found += 1
                title = entry.get('title', 'No Title')
                link = entry.get('link', '')
                
                # Try multiple fields for the published date
                published_date = entry.get('published', entry.get('updated', str(datetime.now())))
                
                # Get a raw summary/description if available
                # feedparser often puts full content in 'content', or summary in 'summary'
                original_summary = entry.get('summary', entry.get('description', ''))
                # Clean HTML tags roughly if it's too long, but we let AI processor handle deep summary later
                
                if not link:
                    continue # Link is mandatory for primary key hash
                
                # Try to insert
                inserted = database.insert_article(
                    title=title,
                    link=link,
                    published_date=published_date,
                    source=source_title,
                    category=category,
                    original_summary=original_summary
                )
                
                if inserted:
                    total_inserted += 1

    logger.info(f"Crawler finished. Found: {total_found}, Inserted (NEW): {total_inserted}, Failed Feeds: {failed_feeds}")
    return total_inserted

if __name__ == "__main__":
    # Ensure database is set up before crawling
    database.init_db()
    run_crawler()
