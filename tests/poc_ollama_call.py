import requests
import json
import time
import re

def test_ollama_connection():
    print("=== [Architecture Step 4] Ollama Local API 검증 PoC ===")
    
    url = "http://localhost:11434/api/generate"
    
    dummy_news_title = "[단독] 애플, 새로운 온디바이스 AI 칩 M5 발표... 전력 효율 극대화"
    dummy_news_body = "애플이 차세대 실리콘 칩인 M5를 공개했다. 이 칩은 로컬 NPU 성능을 기존 대비 30% 끌어올려 외부 클라우드 연결 없이도 아이폰과 맥북 내에서 대규모 언어 모델을 초고속으로 구동할 수 있다. 특히 배터리 소모를 극단적으로 줄이는 아키텍처를 도입하여 AI PC 시장의 게임 체인저가 될 전망이다."
    
    prompt = f"""
    아래 뉴스 기사를 읽고, 한국어로 150자 이내로 요약하고, 관련 키워드를 추출하여 태그로 만들어주세요.
    결과물은 반드시 다른 말 없이 아래 JSON 형식으로만 반환하세요. 마크다운(```json) 블록도 사용하지 말고 오직 순수한 JSON 텍스트 파싱 가능 구문만 출력하세요.
    태그는 딱 3개까지만 만드세요.
    
    [JSON 형식]
    {{
      "summary": "한국어 요약 결과",
      "tags": ["태그1", "태그2", "태그3"]
    }}
    
    [뉴스 제목] {dummy_news_title}
    [뉴스 본문] {dummy_news_body}
    """
    
    payload = {
        "model": "gemma3:4b", 
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0
        }
    }
    
    start_time = time.time()
    
    try:
        print(f">> 타겟 모델 (gemma3:4b) 에 요청을 보냅니다... (최대 30초 대기)")
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        end_time = time.time()
        result = response.json()
        raw_target = result.get("response", "").strip()
        
        print("\n[연결 성공!]")
        print(f"- 응답 소요 시간: {end_time - start_time:.2f}초")
        print("\n[Ollama Native Response (JSON String)]:")
        print(raw_target)
        
        # 클렌징 처리 (Markdown 백틱 제거)
        clean_json = re.sub(r'```json\s*|\s*```', '', raw_target).strip()
        
        try:
            parsed_json = json.loads(clean_json)
            print("\n✅ 검증 통과(Pass): JSON 파싱이 완벽하게 성공했습니다.")
            print("--- 파싱 결과 ---")
            print(f"- 요약: {parsed_json.get('summary')}")
            print(f"- 태그: {parsed_json.get('tags')}")
        except json.JSONDecodeError:
            print("\n❌ 검증 실패(Fail): 클렌징 후에도 JSON 파싱에 실패했습니다.")
            
    except requests.exceptions.Timeout:
        print("\n❌ 검증 실패(Fail): 30초 Timeout이 발생했습니다.")
    except Exception as e:
        print(f"\n❌ 작동 에러: {e}")

if __name__ == "__main__":
    test_ollama_connection()
