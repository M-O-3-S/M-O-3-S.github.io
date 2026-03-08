import feedparser
import time

def test_all_rss_feeds():
    print("=== [Architecture Step 4] User Target RSS Feeds Parsing 검증 ===")
    
    test_urls = [
        # 1. 엣지/임베디드 AI
        "https://www.edge-ai-vision.com/feed/",
        "https://www.embedded.com/feed/",
        "https://www.hackster.io/news.atom",
        "https://www.kdnuggets.com/feed",
        # 2. AI 개발도구
        "https://github.blog/feed/",
        "https://huggingface.co/blog/feed.xml",
        "https://simonwillison.net/atom/everything/",
        "https://newsletter.pragmaticengineer.com/feed",
        # 3. 거대 언어 모델 (LLM)
        "https://tldr.tech/api/rss/ai",
        "https://bair.berkeley.edu/blog/feed.xml",
        "https://lastweekin.ai/feed",
        "https://machinelearningmastery.com/blog/feed/",
        # 4. AI 하드웨어/반도체
        "https://semiengineering.com/feed/",
        "https://www.eetimes.com/feed/",
        "https://spectrum.ieee.org/feeds/feed.rss",
        "https://blogs.nvidia.com/feed/",
        # 5. 로보틱스/자율주행
        "https://www.therobotreport.com/feed/",
        "https://www.aiweirdness.com/rss/",
        # 6. AI 비즈니스/트렌드
        "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "https://www.aitimes.com/rss/allArticle.xml",
        "https://analyticsindiamag.com/feed/",
        # 7. AI 연구/논문
        "https://rss.arxiv.org/rss/cs.AI",
        "https://rss.arxiv.org/rss/cs.LG",
        "https://aws.amazon.com/blogs/machine-learning/feed/"
    ]
    
    success_count = 0
    fail_count = 0
    
    # Add User-Agent header to bypass bot detection for certain websites like Arxiv, AnalyticsIndia
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    for url in test_urls:
        print(f"\n>> 요청 중: {url}")
        try:
            feed = feedparser.parse(url, agent=user_agent)
            
            if 'status' in feed and feed.status not in [200, 301, 302, 308]:
                print(f"  ❌ 실패 (HTTP {feed.status})")
                fail_count += 1
                continue
                
            entries = feed.entries
            if not entries:
                print("  ❌ 실패 (기사 0개 - 차단 또는 규격 오류)")
                fail_count += 1
                continue
                
            print(f"  ✅ 성공 (최신 기사: {entries[0].get('title', 'N/A')[:30]}...)")
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ 치명적 에러: {e}")
            fail_count += 1

    print("\n" + "="*50)
    print(f"🎯 총 {len(test_urls)}개 피드 중 성공: {success_count}개, 통신 실패: {fail_count}개")
    print("="*50)

if __name__ == "__main__":
    test_all_rss_feeds()
