# 아키텍처 4단계: 핵심 리스크 검증 (Architecture Evaluation - PoC)

본 문서는 **[AI News Archive: 아키텍트의 8단계 실행 계획서]**의 4단계 산출물입니다.
본 개발(5단계)에 착수하기 전, 아키텍처 설계가 현실에서 동작 가능한지 가장 얇은 단위(Spike)의 스크립트들을 통해 네 가지 킬러 리스크(Killer Risks)를 조기 검증합니다.

---

## 검증 대상 코어 리스크 (Core Risks)
1.  **AI 추론 검증 (LLM Parsing):** 로컬 환경의 Ollama 모델이 파이썬 위에서 우리가 지정한 정형 구조(JSON)로 알맞게 반환하는가?
2.  **데이터 소스 검증 (RSS Fetching):** Python 라이브러리가 타겟 언론사들의 서로 다른 XML 규격(RSS 2.0, Atom 등)을 통합 포맷으로 파싱할 수 있는가?
3.  **알림 연동 검증 (Telegram API):** Python 코드가 텔레그램 봇 API 규격에 맞춰 정상적으로 푸시 메시지를 보낼 수 있는가?
4.  **스케줄링 검증 (Python Schedule):** OS 종속성 없는 `schedule` 모듈이 백그라운드에서 정상 대기 상태로 루프(Loop)를 도는가?

---

## 1. PoC-1: 로컬 LLM 연동 검증 (`tests/poc_ollama_call.py`)

```python
import requests
import json
import time

def test_ollama_connection():
    print("=== [Architecture Step 4] Ollama Local API 검증 PoC ===")
    
    url = "http://localhost:11434/api/generate"
    
    # 더미 뉴스 데이터
    dummy_news_title = "[단독] 애플, 새로운 온디바이스 AI 칩 M5 발표... 전력 효율 극대화"
    dummy_news_body = "애플이 차세대 실리콘 칩인 M5를 공개했다. 이 칩은 로컬 NPU 성능을 기존 대비 30% 끌어올려 외부 클라우드 연결 없이도 아이폰과 맥북 내에서 대규모 언어 모델을 초고속으로 구동할 수 있다. 특히 배터리 소모를 극단적으로 줄이는 아키텍처를 도입하여 AI PC 시장의 게임 체인저가 될 전망이다."
    
    # 벤(AI Engineer)의 프롬프트 초안 시뮬레이션
    prompt = f"""
    아래 뉴스 기사를 읽고, 한국어로 150자 이내로 요약하고, 관련 키워드를 추출하여 태그로 만들어주세요.
    결과물은 반드시 다른 말 없이 아래 JSON 형식으로만 반환하세요.
    
    [JSON 형식]
    {{
      "summary": "한국어 요약 결과",
      "tags": ["태그1", "태그2", "태그3"]
    }}
    
    [뉴스 제목] {dummy_news_title}
    [뉴스 본문] {dummy_news_body}
    """
    
    payload = {
        "model": "gemma3:4b",  # 타겟 모델명
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1 # 최대한 환각을 줄이고 결정론적인 대답을 받기 위함
        }
    }
    
    start_time = time.time()
    
    try:
        print(f">> 타겟 모델 (gemma3:4b) 에 요청을 보냅니다... (최대 30초 대기)")
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        end_time = time.time()
        result = response.json()
        
        print("\n[연결 성공!]")
        print(f"- 응답 소요 시간: {end_time - start_time:.2f}초")
        print("\n[Ollama Native Response (JSON String)]:")
        print(result.get("response", ""))
        
        # JSON 파싱 검증 (로직이 죽는지 안죽는지 확인)
        try:
            parsed_json = json.loads(result.get("response", ""))
            print("\n✅ 검증 통과(Pass): JSON 파싱이 완벽하게 성공했습니다.")
            print("--- 파싱 결과 ---")
            print(f"- 요약: {parsed_json.get('summary')}")
            print(f"- 태그: {parsed_json.get('tags')}")
        except json.JSONDecodeError:
            print("\n❌ 검증 실패(Fail): 모델이 JSON 규격을 지키지 않았습니다. 추가 클렌징 로직이나 프롬프트 조율이 필요합니다.")
            
    except requests.exceptions.Timeout:
        print("\n❌ 검증 실패(Fail): 30초 Timeout이 발생했습니다. 모델이 너무 느리거나 떠있지 않습니다.")
    except Exception as e:
        print(f"\n❌ 작동 에러: {e}\n  (Ollama가 실행 중인지 확인하세요: http://localhost:11434/)")

if __name__ == "__main__":
    test_ollama_connection()
```

---

## 2. PoC-2: RSS 피드 파싱 검증 (`tests/poc_rss_parsing.py` 작성 완료)
*   **리스크:** 각 언론사마다 RSS/Atom 규격이 미묘하게 다름. XML 데이터 구조 파편화 문제.
*   **검증 목표:** `feedparser` 모듈이 URL 통신 에러 없이 일관된 제목(Title), 링크(Link), 발행일(Published)을 추출해 낼 수 있는지 확인.

## 3. PoC-3: 텔레그램 API 알림 검증 (`tests/poc_telegram_msg.py` 작성 완료)
*   **리스크:** HTTPS 외부 통신 차단 여부 및 Telegram Bot API 인증 (Token, Chat ID) 구조 파악.
*   **검증 목표:** `requests.post()` 를 활용하여 텍스트 및 링크가 포함된 더미 알람을 텔레그램 봇으로 실제 발송.

## 4. PoC-4: 범용 스케줄러 검증 (`tests/poc_schedule_loop.py` 작성 완료)
*   **리스크:** `cron` 없이 `schedule` 모듈 파이썬 프로세스가 죽지 않고 대기 상태(Pending)를 유지하는가.
*   **검증 목표:** 짧은 주기(예: 매 5초)로 예약된 더미 함수가 Time Sleep 블록 구조에서 정상 실행되는지 확인.

---

## 5. 검증 전략 (다음 액션 단계)
개발팀(데이비드/에밀리)은 5단계 구현을 정식 시작하기 전에, 위 명시된 `tests/` 폴더 내의 PoC 파이썬 스크립트들을 모두 하나씩 Run 하여 **4대 핵심 리스크**를 완전히 해소해야 합니다. 모든 스크립트가 Pass 되면, 본 모듈(`crawler.py`, `processor.py` 등) 작성을 시작합니다.
