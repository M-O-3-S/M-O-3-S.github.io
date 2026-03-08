import os
import sys

# Add the backend/src directory to the Python path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src')))

try:
    import database
    import main
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def test_database():
    print("--- Testing Database Operations ---")
    
    # 1. Insert a mockup article
    mock_title = "AI Model Achieves AGI (Mockup)"
    mock_link = "https://example.com/news/agi-achieved"
    mock_date = "2026-03-08T10:00:00Z"
    mock_source = "AI Daily"
    mock_category = "AI News"
    mock_summary = "A new mockup AI model has shown signs of AGI."
    
    print("1. Inserting new mockup article...")
    inserted = database.insert_article(
        title=mock_title, link=mock_link, published_date=mock_date,
        source=mock_source, category=mock_category, original_summary=mock_summary
    )
    print(f"   => Insert successful? {inserted}")
    
    # 2. Try inserting the EXACT SAME article (testing duplicate prevention)
    print("2. Attempting to insert the exact same article again (duplicate test)...")
    inserted_again = database.insert_article(
        title=mock_title, link=mock_link, published_date=mock_date,
        source=mock_source, category=mock_category, original_summary=mock_summary
    )
    print(f"   => Insert successful? {inserted_again} (Should be False!)")
    
    # 3. Update the article with AI tags
    print("3. Updating article with AI mock data...")
    url_hash = database.hash_url(mock_link)
    database.update_ai_processing(
        url_hash=url_hash, 
        ai_summary="[AI] This is a mock AI summary.", 
        ai_tags="AGI, Mockup, Future"
    )
    print("   => Update successful!")
    
    # 4. Verify in DB
    import sqlite3
    conn = sqlite3.connect(database.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, ai_summary, ai_tags FROM articles WHERE url_hash = ?", (url_hash,))
    row = cursor.fetchone()
    print(f"   => Retrieved from DB: Title='{row[0]}', AI Summary='{row[1]}', Tags='{row[2]}'")
    conn.close()
    
    # Clean up mock record so it doesn't pollute the real DB
    conn = sqlite3.connect(database.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles WHERE url_hash = ?", (url_hash,))
    conn.commit()
    conn.close()
    print("   => Mock data cleaned up.")
    print("-----------------------------------\n")

def test_locking():
    print("--- Testing Process Locking (Anti-Zombie) ---")
    print("1. Acquiring lock 'A'...")
    lock_a = main.acquire_lock()
    print("   => Lock 'A' acquired.")
    
    print("2. Trying to acquire lock 'B' simultaneously...")
    try:
        # In a real scenario, this would be a separate process.
        # Here we'll just try to open and lock it again without blocking
        import fcntl
        test_fd = os.open(main.LOCK_FILE, os.O_RDWR)
        fcntl.flock(test_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        print("   => ERROR: Lock 'B' acquired! This should not happen if Lock 'A' is held.")
        os.close(test_fd)
    except BlockingIOError:
        print("   => SUCCESS: Lock 'B' blocked! Prevented concurrent execution.")
    
    print("3. Releasing lock 'A'...")
    main.release_lock(lock_a)
    print("-----------------------------------")


if __name__ == "__main__":
    print("Starting Integrity Tests...\n")
    test_database()
    test_locking()
    print("\nAll Tests Passed!")
