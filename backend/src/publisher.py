import sqlite3
import json
import os
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv
import database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - PUBLISHER - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables for Telegram
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'data')
DAILY_DIR = os.path.join(DATA_DIR, 'daily')
WEEKLY_DIR = os.path.join(DATA_DIR, 'weekly')
TAGS_DIR = os.path.join(DATA_DIR, 'tags')
INDEX_FILE = os.path.join(DATA_DIR, 'index.json')

def ensure_directories():
    os.makedirs(DAILY_DIR, exist_ok=True)
    os.makedirs(WEEKLY_DIR, exist_ok=True)
    os.makedirs(TAGS_DIR, exist_ok=True)

def send_telegram_alert(message):
    """Sends a message via Telegram Bot API."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram credentials not configured. Skipping alert.")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Telegram alert sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")

def generate_daily_json(run_date_str):
    """Exports unpublished, AI-processed articles into a daily JSON file."""
    conn = sqlite3.connect(database.DB_PATH)
    cursor = conn.cursor()
    
    # We select articles processed by AI but not yet published
    cursor.execute('''
        SELECT url_hash, title, link, published_date, source, category, ai_summary, ai_tags
        FROM articles 
        WHERE ai_summary IS NOT NULL AND is_published = FALSE
    ''')
    
    rows = cursor.fetchall()
    
    if not rows:
        logger.info("No new processed articles to publish.")
        conn.close()
        return 0
        
    articles = []
    url_hashes = []
    
    for row in rows:
        url_hashes.append(row[0])
        articles.append({
            "id": row[0],
            "title": row[1],
            "link": row[2],
            "published_date": row[3],
            "source": row[4],
            "category": row[5],
            "ai_summary": row[6],
            # Convert comma separated string back to list
            "ai_tags": [tag.strip() for tag in row[7].split(',')] if row[7] else []
        })
        
    # Write to daily JSON
    daily_filename = f"{run_date_str}.json"
    daily_path = os.path.join(DAILY_DIR, daily_filename)
    
    with open(daily_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Generated {daily_path} with {len(articles)} articles.")
    
    # Update index.json
    update_index_json(run_date_str)
    
    # Mark as published
    cursor.executemany('UPDATE articles SET is_published = TRUE WHERE url_hash = ?', [(h,) for h in url_hashes])
    conn.commit()
    conn.close()
    
    # Send Telegram Teaser (Max 3 articles)
    teaser_msg = f"📰 <b>AI News Archive Daily Update ({run_date_str})</b>\n\n"
    for i, a in enumerate(articles[:3]):
        teaser_msg += f"• <a href='{a['link']}'>{a['title']}</a>\n"
        teaser_msg += f"  <i>{a['ai_tags'][0] if a['ai_tags'] else a['category']}</i>\n\n"
    if len(articles) > 3:
        teaser_msg += f"...and {len(articles)-3} more articles! Check the web archive."
        
    send_telegram_alert(teaser_msg)
    
    return len(articles)

def update_index_json(new_daily_date):
    """Maintains an index.json mapping accessible dates for the frontend."""
    index_data = {"available_dates": []}
    
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        except Exception:
            pass
            
    dates = index_data.get("available_dates", [])
    if new_daily_date not in dates:
        dates.append(new_daily_date)
        
    # Sort descending (newest first)
    dates.sort(reverse=True)
    
    # Keep only the last 90 days in index (retention policy from plan)
    dates = dates[:90]
    index_data["available_dates"] = dates
    
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

def generate_tags_json():
    """Groups recent 30 days published articles by tag and saves to tags/ directory."""
    conn = sqlite3.connect(database.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT url_hash, title, link, published_date, source, category, ai_summary, ai_tags
        FROM articles 
        WHERE is_published = TRUE AND collected_at >= datetime('now', '-30 days')
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    tag_dict = {}
    for row in rows:
        tags = [tag.strip() for tag in row[7].split(',')] if row[7] else []
        article_obj = {
            "id": row[0],
            "title": row[1],
            "link": row[2],
            "published_date": row[3],
            "source": row[4],
            "category": row[5],
            "ai_summary": row[6],
            "ai_tags": tags
        }
        for t in tags:
            if not t: continue
            if t not in tag_dict:
                tag_dict[t] = []
            tag_dict[t].append(article_obj)
            
    for t_val, articles in tag_dict.items():
        # Sort by published date descending
        articles.sort(key=lambda x: x['published_date'], reverse=True)
        # safe filename: alphanumeric, lowercased, spaces to underscores
        safe_tag = "".join(c for c in t_val if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_').lower()
        if not safe_tag: continue
        tag_path = os.path.join(TAGS_DIR, f"{safe_tag}.json")
        with open(tag_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
            
    logger.info(f"Generated JSON files for {len(tag_dict)} tags.")

def generate_weekly_json():
    """Weekly summary generation. Aggregates the last 7 days of articles, picks top tags per category, and selects top 3 articles per category."""
    conn = sqlite3.connect(database.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT url_hash, title, link, published_date, source, category, ai_summary, ai_tags
        FROM articles 
        WHERE is_published = TRUE AND collected_at >= datetime('now', '-7 days')
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        logger.info("No articles found for weekly summary.")
        return

    # 1. Group by category -> count tags -> top tag
    from collections import defaultdict, Counter
    cat_tag_counter = defaultdict(Counter)
    cat_articles = defaultdict(list)
    
    for row in rows:
        cat = row[5]
        tags = [t.strip() for t in row[7].split(',')] if row[7] else []
        
        article_obj = {
            "id": row[0],
            "title": row[1],
            "link": row[2],
            "published_date": row[3],
            "source": row[4],
            "category": cat,
            "ai_summary": row[6],
            "ai_tags": tags
        }
        cat_articles[cat].append(article_obj)
        for t in tags:
            if t: cat_tag_counter[cat][t] += 1
            
    weekly_data = []
    
    for cat, articles in cat_articles.items():
        if not cat_tag_counter[cat]:
            continue
        top_tag = cat_tag_counter[cat].most_common(1)[0][0]
        # filter articles with this tag
        filtered = [a for a in articles if top_tag in a['ai_tags']]
        # sort by date
        filtered.sort(key=lambda x: x['published_date'], reverse=True)
        # take top 3
        top_3 = filtered[:3]
        
        # Add flag to indicate it's weekly top 3 for frontend styling
        for i, a in enumerate(top_3):
            a['is_top_3'] = True
            a['rank'] = i + 1
            a['weekly_hot_tag'] = top_tag
            weekly_data.append(a)
            
    # overall sorting by date
    weekly_data.sort(key=lambda x: x['published_date'], reverse=True)
    
    today = datetime.now()
    week_num = today.isocalendar()[1]
    year = today.year
    weekly_filename = f"{year}_W{week_num}.json"
    weekly_path = os.path.join(WEEKLY_DIR, weekly_filename)
    
    with open(weekly_path, 'w', encoding='utf-8') as f:
        json.dump(weekly_data, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Generated Weekly Report: {weekly_filename} with {len(weekly_data)} articles.")
    
    # Send Telegram
    msg = f"🏆 <b>Weekly Top AI News Available! (Week {week_num})</b>\n\n"
    for a in weekly_data:
        msg += f"[{a['rank']}위 - {a['category']}] <a href='{a['link']}'>{a['title']}</a> (#{a['weekly_hot_tag']})\n\n"
    msg += f"Check the web archive for details."
    send_telegram_alert(msg)

def publish(mode='daily'):
    ensure_directories()
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    if mode == 'daily':
        generate_daily_json(today_str)
        generate_tags_json()
    elif mode == 'weekly':
        generate_weekly_json()

if __name__ == "__main__":
    publish('daily')
