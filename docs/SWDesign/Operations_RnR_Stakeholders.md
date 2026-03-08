# 시스템 운영 및 유지보수 R&R (Roles & Responsibilities)

본 문서는 **[AI News Archive]** 시스템이 성공적으로 개발 완료되어 라이브(Live) 배포가 이루어진 이후, 안정적인 장기 운영을 위해 각 주요 이해관계자(Stakeholder)들이 인계받아야 할 **운영(Operations) 및 유지보수(Maintenance) 역할 명세서**입니다.

이 원칙은 각 직무가 본연의 전문성을 발휘하면서, 보안 사고나 인프라 장애 발생 시 명확하게 책임을 규명하고 신속한 대처가 가능하게 하는 가이드라인(Ground Rule)입니다.

---

## 1. 사라 (Sara) - 프로덕트 매니저 (PO/PM)

*   **포지션(Position):** 전체 프로젝트 총괄 / 프로덕트 오너 (PO) / 품질 관리자
*   **주요 R&R (Roles & Responsibilities):**
    *   **서비스 방향성 승인:** 추가될 새로운 트렌드나 RSS 피드의 채택/반려를 최종 승인.
    *   **품질 보증 파이널 리뷰어 (QA):** LLM이 요약해 낸 뉴스들의 퀄리티가 만족스러운지 주 단위로 로깅/샘플 검토(Audit).
    *   **장애 발생 시 컨트롤 타워:** GitHub Actions 배포 실패나 데이터 수집 오류 등 인시던트(Incident) 리포팅 시, 대응 우선순위를 결정하고 개발팀/기획팀을 조율.
    *   **아키텍처 스케일업 권한:** 만약 GitHub Pages의 트래픽 한도(100GB/월) 초과나 SQLite DB 용량 이슈가 발생하면 예산(Budget) 배정 여부를 기획.

## 2. 제니 & 코니 (Jenny & Koni) - 핵심 사용자 (Consumers)

*   **포지션(Position):** 프론트라인 사용자 그룹 / 텔레그램 채널 운영자 지원
*   **주요 R&R (Roles & Responsibilities):**
    *   **텔레그램 플랫폼 소유권(Owner):** 코니는 `@BotFather`를 통한 봇 생성 관리 등 대외 채널의 권한을 통제하며, 비밀 Token만 추출해 마이클에게 전달.
    *   **뉴스 큐레이션 관리 (User-friendly Config):** 개발자 도움 없이 직접 `backend/config/config.yml` 설정 파일을 열람/수정하여 시스템 제어.
        *   **언제:** 아침 발송 시각 변경
        *   **어디서:** 수집을 원하는 새로운 뉴스 사이트 추가/삭제
        *   **무엇을:** 백엔드 AI 두뇌 업그레이드 여부 결정 (`llm_model` 수정)

## 3. 마이클 (Michael) - 시스템 아키텍트 & 보안 (Security)

*   **포지션(Position):** 인프라 총괄 / 보안 책임자 (Security Officer)
*   **주요 R&R (Roles & Responsibilities):**
    *   **설정 파일 접근 권한 통제 (`.env` 금고지기):**
        *   코니가 생성한 텔레그램 봇의 API 토큰 등 시스템 접속용 민감 정보(`.env`)를 Mac Mini 서버 내부에 직접 삽입하고, 권한(chmod)을 통제하여 시스템 유출을 철저히 방어.
    *   **하드웨어 리소스 및 폴백 로직 모니터링:** M4 Mac Mini 서버의 VRAM, 스토리지가 여유로운지 정기적으로 검토하고, Ollama의 Retry/Fallback 로직이 올바르게 구동되는지 예외 케이스(Exception Log)를 파악.
    *   **운영 체제 종속성 탈피:** `scheduler.py` 가 Mac/Linux 상관없이 안정적으로 24시간 도는지 `cron`/백그라운드 스크립트 상태 확인.

## 4. 에밀리 (Emily) - AI 및 데이터 엔지니어

*   **포지션(Position):** 로컬 모델 품질 최적화 전문가
*   **주요 R&R (Roles & Responsibilities):**
    *   **LLM 파이프라인 (Processor) 모니터링:** 오프라인 모델(Ollama API)이 뱉어내는 JSON 응답에서 불필요한 마크다운(\`\`\`)이나 텍스트 깨짐, 300자 초과 등 텍스트 클렌징 규약 누락이 발생하는지 주기적으로 데이터 통계 확인.
    *   **프롬프트(Prompt) 고도화:** 뉴스 요약이 부자연스럽거나 태그 분류가 부정확할 경우, 시스템 프롬프트를 재설계하여 PM(사라)에게 최적화 방안 제안.
    *   **차세대 모델 리서치:** 사용자(코니/제니)가 `config.yml`로 모델을 스왑하기 이전에, `Llama 3.2 8B` 나 모델의 성능을 로컬 단위로 사전 테스트하고 승인을 권고하는 역할.

## 5. 데이비드 (David) - 백엔드 개발자

*   **포지션(Position):** 파이썬 파이프라인(엔진) 유지보수자
*   **주요 R&R (Roles & Responsibilities):**
    *   **데이터 파이프라인 버그 패치:** RSS 통신(`crawler.py`)이나, DB 저장(`database.py`), JSON 파일 생성(`publisher.py`) 등 3레이어 파이썬 파일 간 로직이 다운되거나 예외(Error) 전파를 막는 코드(Try-Catch) 보완.
    *   **DB 효율성 관리 (Retention & Vacuum):** 코어 저장소인 `news_archive.db`가 커지지 않게끔 정해진 기준 일수 이후 데이터 압축(Vacuum)이 원활하게 구동되고 있는지 확인.
    *   **CI/CD 연동 유지보수:** 백엔드가 최종 결과물(`*.json`)을 찍어낸 후 `deploy.sh`를 통해 정상적으로 `git commit & push` 되도록 터미널 로깅 확인.

## 6. 리암 (Liam) - 프론트엔드 개발자

*   **포지션(Position):** 클라이언트 성능 최적화 담당자 (DOM 제어 전담)
*   **주요 R&R (Roles & Responsibilities):**
    *   **Data Contract 준수 방어:** 백엔드가 생성한 Static JSON 파일 명세와 자바스크립트 DOM 파싱 간섭이 일어나는 경우 즉시 프론트엔드 예외 처리(`Not Found` 등 UI) 로직 보강.
    *   **클라이언트 부하 방지 (Lazy Loading):** 데일리 파일이나 위클리 파일 수량이 1년, 3년 치 누적됨에 따라 브라우저 메모리에 트래픽 폭탄이 일어나지 않도록 메타데이터(`index.json`) 최적화 로드 로직 점검.

## 7. 크리스 (Chris) - UX/UI 디자이너

*   **포지션(Position):** 사용자 경험 및 시각 인터페이스 담당자
*   **주요 R&R (Roles & Responsibilities):**
    *   **UI/UX 디자인 및 퍼블리싱 가이드:** 색상, 타이포그래피, 다크모드/라이트모드 정책 등 사용자가 닿는 모든 화면의 시각 디자인 가이드 수립. 리암은 오직 크리스의 가이드대로 CSS를 구성.
    *   **반응형 레이아웃 검증:** PC 및 모바일 화면에서 메뉴와 콘텐츠가 직관적으로 배치되는지 확인하고 개선안 마련.

---

### 기타 규칙 (Operations Ground Rule)

*   **장애 전파 체계 (Escalation Path):** 크롤링 실패(`David`), 렌더링 깨짐(`Liam`), 디자인 가이드 위반(`Chris`), 요약품질 저하(`Emily`), 스케줄링 마비(`Michael`) 등 오류 발생 시, **담당자가 최우선으로 리포트하고, 필요 시 PM(사라)에게 보고 후 승인을 거쳐 Hotfix(긴급 배포)를 진행합니다.**
*   `config.yml`의 주요 정보(RSS 타겟팅 추가, 변경 등)는 사용자(제니/코니)가 단독 갱신 후 사내 메신저를 통해 전체 시스템 구동 정상 여부를 마이클에게 알림(Notification)합니다.
