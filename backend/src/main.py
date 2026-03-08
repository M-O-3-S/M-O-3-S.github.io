import argparse
import logging
import os
import sys
import fcntl
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('main_pipeline')

LOCK_FILE = os.path.join(os.path.dirname(__file__), '..', '.pipeline.lock')

def acquire_lock():
    """Acquires a file lock to prevent concurrent executions."""
    try:
        lock_fd = os.open(LOCK_FILE, os.O_CREAT | os.O_RDWR)
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        logger.info("Lock acquired successfully. No competing processes found.")
        return lock_fd
    except BlockingIOError:
        logger.error("Another pipeline instance is already running. Exiting to prevent duplication/zombie processes.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to acquire lock: {e}")
        sys.exit(1)

def release_lock(lock_fd):
    """Releases the file lock."""
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)
        logger.info("Lock released successfully.")
    except Exception as e:
        logger.error(f"Error releasing lock: {e}")

def run_daily_pipeline():
    logger.info("Starting DAILY pipeline...")
    
    # 1. Crawl Feeds
    import crawler
    crawled_count = crawler.run_crawler()
    logger.info(f"Step 1 Complete: {crawled_count} new articles gathered.")
    
    # 2. Process with AI
    import processor
    processed_count = processor.process_articles()
    logger.info(f"Step 2 Complete: {processed_count} articles summarized by AI.")
    
    # 3. Publish to JSON & Notify
    import publisher
    published_count = publisher.publish(mode='daily')
    logger.info(f"Step 3 Complete: {published_count} articles exported to frontend.")
    
    # 4. DB Cleanup (Retention)
    import database
    deleted = database.cleanup_old_records()
    logger.info(f"Step 4 Complete: Database cleanup removed {deleted} old records.")
    
    # 5. Git Deployment
    import deploy
    deploy.deploy_to_github()
    logger.info("Step 5 Complete: Deployment to GitHub triggered.")
    
    logger.info("DAILY pipeline completed successfully.")

def run_weekly_pipeline():
    logger.info("Starting WEEKLY pipeline...")
    import publisher
    publisher.publish(mode='weekly')
    import deploy
    deploy.deploy_to_github()
    logger.info("WEEKLY pipeline completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI News Archive System Entrypoint")
    parser.add_argument('--mode', choices=['daily', 'weekly'], required=True, help='Execution mode')
    args = parser.parse_args()
    
    lock_fd = acquire_lock()
    try:
        # Initialize database first just in case
        import database
        database.init_db()
        logger.info("Database initialized.")
        
        if args.mode == 'daily':
            run_daily_pipeline()
        elif args.mode == 'weekly':
            run_weekly_pipeline()
            
    finally:
        release_lock(lock_fd)
