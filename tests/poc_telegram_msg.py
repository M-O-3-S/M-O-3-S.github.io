import requests
import json
import time

def test_telegram_api():
    print("=== [Architecture Step 4] Telegram API 검증 PoC ===")
    
    # 더미/안전 테스트 환경: 
    # 실제 토큰이 없으므로, API의 구조적 동작성(URL 엔드포인트 도달)과 에러 핸들링 로직만 우선 검증
    dummy_token = "123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"
    dummy_chat_id = "@dummy_ai_news_channel"
    text_message = "🚀 [테스트] 새로운 AI 뉴스가 도착했습니다!\n🔗 https://m-o-3-s.github.io"
    
    url = f"https://api.telegram.org/bot{dummy_token}/sendMessage"
    payload = {
        "chat_id": dummy_chat_id,
        "text": text_message,
        "parse_mode": "HTML"
    }
    
    print(">> 텔레그램 API 서버로 테스트 요청 전송...")
    start_time = time.time()
    try:
        response = requests.post(url, json=payload, timeout=5)
        elapsed = time.time() - start_time
        
        # 401 Unauthorized 등 토큰 오류가 떨어지면 API 연동 자체는 도달한 것임!
        if response.status_code == 401:
            print(f"✅ 검증 통과(Pass): 텔레그램 API 서버 통신 성공! (401 에러는 가짜 토큰이라 당연함. {elapsed:.2f}초)")
        elif response.status_code == 200:
            print("✅ 검증 통과(Pass): 실제 메시지 전송 완벽 성공!")
        else:
            print(f"❌ 검증 실패(Fail): 예상치 못한 HTTP 에러 코드 {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ 검증 실패(Fail): 텔레그램 서버 접근 시간 초과 (방화벽/네트워크 확인 요망)")
    except Exception as e:
        print(f"❌ 검증 실패(Fail): 백엔드 통신 에러 발생 {e}")

if __name__ == "__main__":
    test_telegram_api()
