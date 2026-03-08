import schedule
import time
import subprocess
import os
import yaml
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SCHEDULER - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yml')
MAIN_SCRIPT = os.path.join(os.path.dirname(__file__), 'main.py')

def get_schedule_times():
    daily_time = "07:00"
    weekly_time = "Saturday 08:00"
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)
            daily_time = config.get('schedule', {}).get('daily_time', "07:00")
            weekly_time = config.get('schedule', {}).get('weekly_time', "Saturday 08:00")
    except Exception as e:
        logger.warning(f"Could not read config.yml for scheduling times: {e}. Using defaults.")
    return daily_time, weekly_time

def run_daily_job():
    logger.info("Triggering Daily Job...")
    try:
        # We use subprocess to execute main.py in a clean environment and utilizing its fcntl locking
        subprocess.run(['python', MAIN_SCRIPT, '--mode', 'daily'], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Daily job failed: {e}")

def run_weekly_job():
    logger.info("Triggering Weekly Job...")
    try:
        subprocess.run(['python', MAIN_SCRIPT, '--mode', 'weekly'], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Weekly job failed: {e}")

if __name__ == "__main__":
    daily_time, weekly_time = get_schedule_times()
    
    # Schedule the Daily Job
    logger.info(f"Scheduling daily job at {daily_time}")
    schedule.every().day.at(daily_time).do(run_daily_job)
    
    # Schedule the Weekly Job
    # The config format is "Saturday 08:00"
    try:
        day_str, time_str = weekly_time.split(' ')
        getattr(schedule.every(), day_str.lower()).at(time_str).do(run_weekly_job)
        logger.info(f"Scheduling weekly job on {day_str} at {time_str}")
    except Exception as e:
        logger.error(f"Failed to parse weekly schedule time '{weekly_time}'. Using default Saturday 08:00. Detail: {e}")
        schedule.every().saturday.at("08:00").do(run_weekly_job)

    logger.info("Scheduler is running. Press Ctrl+C to stop.")
    
    while True:
        schedule.run_pending()
        time.sleep(60)
