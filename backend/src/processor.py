import logging
import requests
import json
import sqlite3
import os
import time
import re
from dotenv import load_dotenv
import database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - PROCESSOR - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = os.getenv("LLM_MODEL", "gemma3:4b")

def get_unprocessed_articles():
    """Fetches articles from DB that haven't been processed by AI yet."""
    conn = sqlite3.connect(database.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT url_hash, title, original_summary, category 
        FROM articles 
        WHERE ai_summary IS NULL
        LIMIT 10
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert DB rows to dictionaries
    return [{"url_hash": row[0], "title": row[1], "original_summary": row[2], "category": row[3]} for row in rows]

def generate_prompt(article):
    """Constructs the prompt for the AI model based on our system requirements."""
    content = article.get("original_summary")
    if not content or len(content) < 50:
        # If no summary or too short, use the title
        content = article.get("title")

    system_prompt = f"""You are an expert AI news editor. Your task is to process the following tech news article.
Category Guidelines: The article belongs to the broad category [{article['category']}].

Rules:
1. Write a 3-sentence summary in Korean exactly. No more, no less.
2. The summary MUST be under 300 characters in total length.
3. Extract exactly 1 to 3 keywords (tags) related to the content in English or Korean.
4. Output your response strictly in JSON format as follows:
{{
    "summary": "Your 3-sentence Korean summary here.",
    "tags": ["Tag1", "Tag2", "Tag3"]
}}
Do not include any other text, markdown blocks, or explanations. Just output the raw JSON object.

News Content:
{content}
"""
    return system_prompt

def call_ollama(prompt, model, timeout=30):
    """Calls local Ollama API to generate the summary."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json" # Force JSON mode if model supports it
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        return result.get('response', '')
    except requests.exceptions.Timeout:
        logger.error(f"Ollama API request timed out after {timeout} seconds.")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Ollama API: {e}")
        return None

def parse_ai_response(response_text, original_title, category):
    """Parses JSON response from Ollama safely, with fallback mechanisms."""
    ai_summary = None
    ai_tags = None
    
    # Fallback function
    def apply_fallback():
        return f"[자동 추출] {original_title}", f"[{category}]"
    
    if not response_text:
        return apply_fallback()
        
    try:
        # Strip trailing/leading markdown codeblocks if Ollama wraps them
        clean_text = response_text.strip()
        if clean_text.startswith("```"):
            clean_text = re.sub(r'^```(?:json)?\s*', '', clean_text)
            clean_text = re.sub(r'\s*```$', '', clean_text)
            
        data = json.loads(clean_text)
        ai_summary = data.get("summary", "")
        tags_list = data.get("tags", [])
        
        # Validation checks based on constraints
        if not ai_summary or len(ai_summary) > 400: # generous buffer before fallback
            logger.warning("AI Summary absent or too long. Applying fallback.")
            return apply_fallback()
            
        if not isinstance(tags_list, list) or len(tags_list) > 5:
            tags_list = [category] # fallback for tags
            
        # Clean and truncate tags
        cleaned_tags = []
        for t in tags_list:
            if not isinstance(t, str):
                continue
            # Remove special chars and spaces
            t_clean = re.sub(r'[^a-zA-Z0-9가-힣]', '', t).strip()
            # Truncate to 20 chars
            if len(t_clean) > 20:
                t_clean = t_clean[:20]
            if t_clean and t_clean not in cleaned_tags:
                cleaned_tags.append(t_clean)
                
        if not cleaned_tags:
            cleaned_tags = [category]
            
        ai_tags = ", ".join(cleaned_tags[:3]) # Force max 3 tags
        
        return ai_summary, ai_tags
        
    except json.JSONDecodeError:
        logger.warning(f"Failed to parse AI response as JSON. Raw response: {response_text[:100]}...")
        return apply_fallback()

def process_articles():
    """Main loop to process all pending articles."""
    logger.info("Starting AI Processor Pipeline...")
    
    unprocessed = get_unprocessed_articles()
    total = len(unprocessed)
    
    if total == 0:
        logger.info("No new articles to process.")
        return 0
        
    logger.info(f"Found {total} new articles. Using model: {DEFAULT_MODEL}")
    
    processed_count = 0
    
    for i, article in enumerate(unprocessed, 1):
        url_hash = article['url_hash']
        title = article['title']
        category = article['category']
        
        logger.info(f"Processing ({i}/{total}): {title}")
        
        prompt = generate_prompt(article)
        
        # Attempt 1
        ai_response = call_ollama(prompt, DEFAULT_MODEL, timeout=30)
        
        # Retry mechanism (Max 1 retry)
        if not ai_response:
            logger.info("Attempt 1 failed. Retrying in 3 seconds...")
            time.sleep(3)
            ai_response = call_ollama(prompt, DEFAULT_MODEL, timeout=45) # Longer timeout for retry
            
        # Parse and apply fallbacks
        ai_summary, ai_tags_str = parse_ai_response(ai_response, title, category)
        
        # Update Database
        database.update_ai_processing(url_hash, ai_summary, ai_tags_str)
        processed_count += 1
        
    logger.info(f"AI Processor finished. Successfully processed {processed_count}/{total} articles.")
    return processed_count

if __name__ == "__main__":
    process_articles()
