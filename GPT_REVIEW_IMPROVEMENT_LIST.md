# GPT-5 리뷰 개선 항목 리스트 (AI News Archive)

- 리뷰 수행자: GPT-5 Codex
- 리뷰 일시: 2026-03-08 (KST)
- 리뷰 범위: `docs/`, `backend/src/`, `backend/config/`, `frontend/`, `tests/`
- 작업 원칙: 본 문서는 **리뷰 결과만** 포함하며, 코드/디자인 구현 작업은 수행하지 않음

## 핵심 결론
- 프로젝트는 Daily/Weekly 뉴스 파이프라인과 정적 프론트가 이미 연결된 **초기 구현 단계(POC+)**입니다.
- 다만, 문서 요구사항 대비 운영 안정성/설정 일관성/배포 안전성에서 우선 수정이 필요한 갭이 확인되었습니다.

## 개선 항목 (우선순위 순)

| ID | 우선순위 | 개선 항목 | 근거(파일:라인) | 권장 방향 |
|---|---|---|---|---|
| R-01 | Critical | `news_archive.db`가 Git 추적/배포 범위에 포함됨 | `docs/DEV_Requirements_AI_News_Archive.md:40`, `backend/src/database.py:7`, `backend/src/deploy.py:55`, `backend/src/deploy.py:58`, `git ls-files frontend/data/news_archive.db` 결과 | DB 파일을 배포 아티팩트 경로에서 분리하고, `.gitignore`로 DB/락/환경파일을 명시적으로 제외 |
| R-02 | Major | LLM 모델 교체 설정이 문서와 다르게 동작 | `backend/config/config.yml:3-5`, `docs/System_Manual_AI_News_Archive.md:41-44`, `backend/src/processor.py:21` | `config.yml`의 `system.llm_model`을 단일 소스로 읽고, 필요 시 env는 override 용도로만 사용 |
| R-03 | Major | 설정 스키마 불일치로 일부 설정값이 사실상 무효 | `backend/src/crawler.py:59-60`, `backend/src/database.py:93`, `backend/config/config.yml:1-57` | `settings.*` 스키마를 `config.yml`에 추가하거나 코드 키 경로를 현재 스키마(`system/schedule/rss_feeds`)에 맞춰 통일 |
| R-04 | Major | 배포 충돌 방지(`pull --rebase`) 요구 미구현 | `docs/DEV_Requirements_AI_News_Archive.md:77`, `backend/src/deploy.py:46-49`, `backend/src/deploy.py:73` | push 전 원격 동기화 단계(예: `fetch + pull --rebase`)와 실패 시 중단/롤백 로깅 추가 |
| R-05 | Major | 중복 제거 fallback(정규화 제목+발행일) 미구현 | `docs/PRD_AI_News_Archive.md:40`, `docs/DEV_Requirements_AI_News_Archive.md:72`, `backend/src/database.py:46-57` | URL 해시 외에 정규화 제목+발행일 기준의 보조 중복 키를 추가 |
| R-06 | Major | 초기 구동 시 벌크 수집(Cold Start) 요구 미충족 | `docs/PRD_AI_News_Archive.md:43-44`, `backend/src/crawler.py:87-93` | DB 초기 상태에서만 과거 N일 수집하는 분기 로직(설정 기반) 추가 |
| R-07 | Major | Retention 후 `VACUUM` 미실행 | `docs/DEV_Requirements_AI_News_Archive.md:49`, `docs/DEV_Requirements_AI_News_Archive.md:78`, `backend/src/database.py:100-104` | 삭제 이후 `VACUUM` 수행 및 주기/실행시간을 설정화 |
| R-08 | Major | AI 규칙 위반 시 재시도/태그 규약 준수가 PRD와 부분 불일치 | `docs/PRD_AI_News_Archive.md:63-69`, `backend/src/processor.py:95`, `backend/src/processor.py:116-118`, `frontend/data/index.json:7` | 규칙 위반(300자 초과/태그 개수 초과/형식 불량) 자체를 재시도 트리거로 승격하고, fallback 태그 포맷을 규약형으로 고정 |
| R-09 | Major | 프론트 캘린더/날짜 로직이 2026-03으로 하드코딩됨 | `frontend/index.html:87`, `frontend/index.html:98-128`, `frontend/js/script.js:102`, `frontend/js/script.js:110` | `index.json` 기반 동적 캘린더 렌더링과 월 이동 로직으로 전환 |
| R-10 | Major | Weekly 집계 기간 정의가 PRD 기준(토~금)과 다름 | `docs/PRD_AI_News_Archive.md:106`, `backend/src/publisher.py:214`, `backend/src/publisher.py:269-273` | KST 기준 고정 주차 윈도우(지난 토~금)를 계산해 파일명/집계 데이터 모두 동일 기준으로 맞춤 |
| R-11 | Minor | Daily publish 결과값이 상위 파이프라인 로그에 반영되지 않음 | `backend/src/main.py:55-56`, `backend/src/publisher.py:287-295` | `publish()`가 건수/결과 코드를 반환하도록 인터페이스 정리 |
| R-12 | Minor | 운영 매뉴얼의 시간 정보 및 문장 구조가 실제 설정과 불일치 | `docs/System_Manual_AI_News_Archive.md:38`, `backend/config/config.yml:11`, `docs/System_Manual_AI_News_Archive.md:50-53` | 매뉴얼을 현재 설정/동작과 동기화하고 중복·깨진 문단 정리 |
| R-13 | Minor | 사용자 에러 메시지 언어가 혼합됨 | `frontend/js/script.js:193` | 한국어 메시지로 통일 |

## 참고 메모
- 본 리스트는 “구현 지시서”가 아니라, 제미나이(구현 담당)에게 전달 가능한 **리뷰 백로그** 목적의 문서입니다.
- 우선 적용 순서는 `Critical -> Major -> Minor` 권장입니다.
