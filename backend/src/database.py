import sqlite3
import hashlib
from datetime import datetime
import os
import yaml

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'data', 'news_archive.db')
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yml')

def init_db():
    """Initializes the SQLite database and creates the necessary tables."""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # URL Hash is used as the PRIMARY KEY to completely avoid duplicates at DB level
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            url_hash TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            link TEXT NOT NULL,
            published_date TEXT,
            source TEXT,
            category TEXT,
            original_summary TEXT,
            ai_summary TEXT,
            ai_tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_published BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()
    conn.close()

def hash_url(url: str) -> str:
    """Generates a SHA-256 hash for a given URL."""
    return hashlib.sha256(url.encode('utf-8')).hexdigest()

def insert_article(title, link, published_date, source, category, original_summary):
    """Inserts a new article if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    url_hash = hash_url(link)
    
    try:
        cursor.execute('''
            INSERT INTO articles (url_hash, title, link, published_date, source, category, original_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (url_hash, title, link, published_date, source, category, original_summary))
        conn.commit()
        inserted = True
    except sqlite3.IntegrityError:
        # Article already exists (duplicate)
        inserted = False
        
    conn.close()
    return inserted

def update_ai_processing(url_hash, ai_summary, ai_tags):
    """Updates the article with AI generated summary and tags."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE articles 
        SET ai_summary = ?, ai_tags = ?
        WHERE url_hash = ?
    ''', (ai_summary, ai_tags, url_hash))
    
    conn.commit()
    conn.close()

def mark_as_published(url_hash):
    """Marks an article as published (e.g. sent via JSON)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE articles SET is_published = TRUE WHERE url_hash = ?', (url_hash,))
    
    conn.commit()
    conn.close()

def cleanup_old_records():
    """Deletes records older than retention_days defined in config.yml."""
    
    # Load settings from config
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)
            retention_days = config.get('settings', {}).get('database', {}).get('retention_days', 30)
    except Exception:
        retention_days = 30 # fallback
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f"DELETE FROM articles WHERE created_at < datetime('now', '-{retention_days} days')")
    deleted_count = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return deleted_count

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
