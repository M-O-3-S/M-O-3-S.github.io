# 소프트웨어 아키텍처 설계서 (SW Architecture Design Record)

본 문서는 전통적인 소프트웨어 공학의 8단계 아키텍쳐 설계 방법론을 기반으로 작성된 **"AI News Archive"** 시스템의 마스터 플랜입니다. 시스템의 지속 가능성, 운영 비용, 확장성을 모두 고려하여 작성되었습니다. (작성자: Michael, SW Architect)

---

## 1단계 · 과제 착수 (Initiation)

*   **이해관계자(Stakeholders):** 
    *   **사용자(Consumer):** 제니(Day 1 Retention 중시), 코니(직관성 및 쉬운 요약 중시)
    *   **비즈니스(PO):** 사라 (최소 비용으로 최대 Value 창출, 추후 피보팅 확장성)
    *   **개발/디자인:** 크리스(UX/UI), 리암(FE), 엠마(BE/Data), 벤(AI)
*   **비즈니스 목표:** 개인 또는 소규모 그룹이 소비할 수 있는 매일/매주 AI 뉴스 아카이브 제공.
*   **제약 조건 (Constraints):** 
    *   **예산:** 0원 (Zero-Cost). 서버 호스팅 비, DB 호스팅 비용 불가.
    *   **자원:** 개인용 로컬 M4 Mac Mini만 활용할 것.
*   **시스템 현황:** 신규 구축 과제이므로 레거시는 존재하지 않음.

## 2단계 · 요구사항 분석 (Requirements Analysis)

*   **기능 요구사항 (Functional Requirements - FR):**
    *   다중 RSS 피드 스크래핑 및 파싱.
    *   Local LLM(Ollama) 기반 300자 이내 한국어 요약 및 태그 생성.
    *   정적 HTML/CSS 웹사이트 생성 및 GitHub Pages 배포.
    *   텔레그램 메시지 알림.
*   **비기능 요구사항 (Non-Functional Requirements - NFR):**
    *   **유지보수성(Maintainability):** 스크립트 실행 환경이 깨지더라도 복구가 쉬워야 함.
    *   **가용성(Availability):** AI 모델이나 특정 언론사 RSS가 죽어도 시스템 자체는 뻗지 않아야 함.
    *   **경제성(Cost):** 외부 유료 API 및 클라우드 구독 절대 금지.
*   **품질 속성 우선순위 (Quality Attributes):** Cost(돈) > Maintainability(유지보수) > Availability(가용성) > Performance(성능)

## 3단계 · 아키텍처 설계 (Architecture Design)

*   **아키텍처 스타일:** 모놀리식 스크립트 기반 (Static Site Generator 패턴결합). 불필요한 마이크로서비스(MSA) 배제.
*   **기술 스택 선정:**
    *   **백엔드:** Python 3.10+ (가장 파이프라인 관리가 용이한 언어)
    *   **DB:** SQLite (내장 라이브러리, 별도 서버 불필요, `news_archive.db` 단일 파일)
    *   **AI:** Ollama CLI (`gemma3:4b` 로컬 추론 엔진)
    *   **스케줄링:** macOS 내장 `cron` (불필요한 n8n 무거움 제거)
    *   **프론트엔드/호스팅:** Vanilla JS + CSS + HTML / GitHub Pages
*   **시스템 분해 (모듈화):**
    1.  `crawler` 모듈: 수집과 DB 적재만 담당
    2.  `processor` 모듈: DB 읽기, LLM 연동, 요약 저장만 담당
    3.  `publisher` 모듈: 파일(JSON) 생성 및 알림망, GitHub Push 담당
*   **API 설계 원칙 (인터페이스):**
    *   백엔드와 프론트엔드는 통신 프로토콜(HTTP GET/POST)이 아닌 **"정적 JSON 파일(Data Contract)"**로 통신한다.
    *   프론트엔드의 부하를 줄이기 위해 `/data/daily/YYYY-MM-DD.json` 형태로 날짜별 파일을 쪼개놓는다(Sharding).

## 4단계 · 아키텍처 검증 (Architecture Evaluation)

*   **ADR (Architecture Decision Record) 핵심 요약:**
    *   *결정:* n8n 대신 **macOS cron + 순수 파이썬**을 채택함.
    *   *근거:* n8n은 워크플로우를 그리기 편하지만, 메모리 상주 리소스가 큼. M4 Mac Mini의 리소스를 LLM 추론에 집중시키기 위해 스케줄러 오버헤드를 제로(0)에 가깝게 맞춰야 함.
*   **PoC (Proof of Concept):**
    *   **Frontend PoC:** 리암이 디자인 시스템 기반으로 HTML/CSS/JS 정적 구동을 성공적으로 파일 검증 완료함. (3단계 통과)
    *   **Backend PoC:** (다음 단계 예정) SQLite 연결 및 Ollama REST API 타겟팅 기본 테스트 진행 필요.

## 5단계 · 개발 지원 (Development Support)

*   **개발팀 디렉토리 구조 및 역할 분담 (Contract):**
    *   `backend/src/`: 백엔드(`데이비드`), `FE` 개발과 완전히 격리.
    *   `backend/src/llm/`: 프론트엔드(`에밀리`), 여기서 AI 퀄리티 조정.
    *   `docs/`: 전체 기획 및 설계 산출물 관리.
    *   `frontend/` ➡️ 최상단 이동: 프론트엔드(`리암`), 정적 사이트 소스. 백엔드의 폴더에 개입하지 않음.
    *   `data/`: 백엔드와 프론트엔드가 교차하는 "인터페이스 창고".
*   **코드 리뷰 가이드:** 
    *   에러 발생 시 프로그램 패닉(`sys.exit(1)`) 금지. 로거(Logger)에 남기고 반드시 안전한 Fallback 행동을 취할 것.

## 6단계 · 품질 관리 (Quality Assurance)

*   **아키텍처 적합성 함수 (Fitness Functions):**
    *   *용량 관리:* `SQLite` DB가 일정 사이즈 초과 시 백업 후 Vacuum 처리. 
    *   *파일 제한:* `data/` 내부의 정적 JSON 파일은 30일이 지난 것에 대해 자동 삭제 로직 핑거프린트 포함.
*   **보안 취약점 (Security):** 
    *   Telegram Bot Token을 코드에 하드코딩하지 않고 `.env` 파일로 로드. `feeds.yaml`에 민감한 정보 배제.

## 7단계 · 배포 및 운영 설계 (Deployment & Operations)

*   **CI/CD 파이프라인:** 
    *   매일 오전 7시 파이썬 셸 스트립트 동작 ➡️ JSON 생성 ➡️ `.sh` 스크립트를 통한 `git add data/ && git commit -m "auto" && git push` 자동 수행.
*   **장애 대응 (Failover Scenario):**
    1.  **RSS 소스 죽었을 때:** 크롤러 모듈의 HTTP Timeout(5초) 시도 후, 해당 소스는 Skip 처리 (전체 프로세스 유지).
    2.  **Ollama 응답 지연/할루시네이션:** 최대 30초 대기 후 취소. 1회 재시도 구현. 그래도 실패 시 요약란에 "원문을 참고해주세요." + 태그란에 "일반"을 Fallback으로 찍고 DB 저장 (정상 프로세스 취급).

## 8단계 · 회고 및 진화 (Retrospective & Evolution)

*   **향후 진화 방향:**
    *   현재 구조는 단일 카테고리(AI)에 특화되어 있으나, SQLite 테이블 스키마 설계 시 `theme_id` 나 JSON 파일 명명 규칙(`theme_ai_YYYY-MM-DD.json`)을 열어두어 추후 경제/부동산 카테고리 추가 시 **MSA 없이 모놀리스 내부 모듈만 확장**하여 대응 가능하도록 설계함.
