# 개발 요구 및 제약사항 — AI 뉴스 아카이브

> 본 문서는 AI 뉴스 아카이브 시스템의 개발 요구사항 및 기술 제약사항을 정의한다.
> 제품 요구사항은 별도 문서(PRD_AI_News_Archive)를 참고한다.

---

## 1. 실행 환경

| 항목 | 내용 |
|------|------|
| 실행 환경 | M4 Mac mini 기본형 이상의 저사양 PC에서 동작 가능해야 함 |
| AI 모델 | 로컬 실행 (Ollama) — 외부 API 비용 없음 (초기 `gemma3:4b` 사용 후 `gemma3:9b` 등 7B~12B급 모델로 손쉬운 스왑(Swap) 지원 필수) |
| 웹 배포 (Hosting) | GitHub Pages 활용 — 서버 비용 없음, 정적 파일만 서빙 |
| 웹 UI (Frontend) | CSS Media Queries를 활용하여 **PC(데스크탑) 및 모바일 브라우저를 모두 지원하는 반응형 웹(Responsive Web)** 으로 구현 |

---

## 2. 설정 및 운영 (User-Friendly Config)

> 코니(비개발자 PR 담당) 등 시스템에 대한 기술적 지식이 없는 사용자도 직관적으로 설정을 바꿀 수 있도록, 모든 운영 설정은 **읽기 쉬운 YAML 파일(`backend/config/config.yml`)** 로 통합 관리한다. (단, 텔레그램 봇 토큰 등 보안에 민감한 비밀키만 `.env` 로 분리한다.)

| 항목 | 내용 |
|------|------|
| 타겟 LLM 모델 | `backend/config/config.yml` 내 `llm_model: "gemma3:4b"` 텍스트만 수정하면 백엔드 전체에 즉각 반영됨 |
| RSS 관리 | `backend/config/config.yml` 파일 목록에서 수집할 URL들을 추가·삭제·수정 용이하게 관리 |
| Daily 발송 시각 | `backend/config/config.yml` 파일 내 `schedule.daily_time: "07:00"` 항목으로 손쉽게 변경 가능 |
| Weekly 발송 시각 | `backend/config/config.yml` 파일 내 `schedule.weekly_time: "Saturday 08:00"` 항목으로 손쉽게 변경 가능 |

---

## 3. 내부 데이터 저장소

> 사용자가 직접 접근하거나 조작하는 기능이 아니다. 파이프라인이 자동으로 활용하는 내부 부품이다.

**저장소 유형**
- SQLite 단일 파일 DB를 사용한다. (`news_archive.db`)
- 별도 DB 서버 설치 없이 Python 기본 내장 라이브러리(`sqlite3`)로 운용한다.
- 원문 전체는 저장하지 않으며, 메타데이터 및 처리 결과만 저장한다.
- 로컬 PC 내에서만 존재하며, GitHub에는 업로드되지 않는다.

**시스템이 DB를 사용하는 시점**

| 시점 | DB 사용 목적 |
|------|-------------|
| 매일 수집 시작 전 | 스크립트 중복 실행 방지(Locking 매커니즘) 검토 |
| 매일 오전 7시 수집 시 | 새 기사의 URL 해시를 기존 DB와 비교하여 중복 수집 방지 |
| 매주 토요일 오전 8시 | 일주일치 태그 빈도를 집계하여 Weekly News Top 3 선정 |
| 주기적 Retention 실행 시 | 만료된 과거 데이터(예: 1년 이상) 삭제 후, 반드시 `VACUUM` 명령을 실행하여 물리적 DB 파일 용량을 최적화 |

**저장 항목**

| 필드 | 설명 |
|------|------|
| `url_hash` | URL 기반 중복 체크용 해시 (Primary Key) |
| `title` | 기사 제목 |
| `source` | RSS Feed 출처명 |
| `url` | 원문 기사 URL |
| `published_at` | 기사 발행일시 |
| `category` | AI 분류 카테고리 |
| `summary` | AI 생성 요약 (최대 300자) |
| `tags` | AI 생성 태그 목록 |
| `collected_at` | 시스템 수집 일시 |

---

## 4. 데이터 처리 및 파이프라인

| 항목 | 내용 |
|------|------|
| 예외 처리 (수집) | RSS 피드 요청 시 Connection Timeout(예: 10초)을 설정하고, 특정 피드 실패 시 전체 파이프라인이 중단되지 않고 Skip 하도록 방어 |
| 중복 처리 | URL 해시(MD5) 기반 중복 수집 방지, fallback으로 정규화된 제목+발행일 조합 사용 |
| 예외 처리 (AI) | 로컬 모델(Ollama) 추론 지연 방지를 위한 Timeout 설정, 프롬프트 위반 시 1회 Retry 및 기본값 폴백(Fallback) 로직 필수 구현 |
| AI 모델 교체성 | 시스템의 코드 수정 없이, `backend/config/config.yml` 등의 설정 파일에서 모델명 스트링(예: `gemma3:4b` -> `llama3.2`)만 변경하면 LLM이 즉각 교체되는 유연한 구조 보장 |
| 유지보수성 (DevOps) | 로컬 PC(Mac Mini)에서 `backend/src/main.py` 실행 시 자동으로 HTML 배포까지 원클릭으로 완료되는 쉘 스크립트 제공 |
| AI 문자열 정제 (Cleansing) | AI 모델이 반환한 태그 문자열에서 특수문자를 제거하고, 띄어쓰기를 강제로 없애며, 비정상적으로 긴 태그(20자 초과)는 잘라내는(Truncate) 백엔드 파이프라인 후처리 및 마크다운(\`\`\`json) 강제 삭제 정규식 필수 구현 |
| 배포 충돌 방지 (Git) | GitHub Pages 자동 배포 스크립트 실행 시, 로컬 변경사항을 `git commit & push` 하기 직전에 반드시 원격 저장소와 동기화(`git pull --rebase` 등)하여 Git Conflict 파이프라인 중단 사태를 방어 |
| 원문 및 DB 보존 | 데이터베이스 비대화 방지를 위해 1년 등 일정 기간이 지난 과거 데이터 삭제(Retention) 스크립트 주기적 실행 및 DB Vacuum 수행 |
| JSON 데이터 분할 | 정적 사이트(GitHub Pages) 성능을 위해 발행 데이터는 `All.json`이 일자별(`daily/YYYY-MM-DD.json`), 태그별(`tags/tag_name.json`), 인덱스(`index.json`)로 분할하여 빌드 |
| JSON 용량 제한 | 프론트엔드 과부하를 막기 위해 태그별 JSON(`tags/tag_name.json`)은 전체 데이터가 아닌 **최근 30일치 데이터만 포함**하도록 사이즈를 제한하여 빌드 |
| 예외 처리 (FE) | 정적 사이트 특성상 비동기로 JSON을 가져오므로, 텔레그램 링크를 트고 들어온 앵커 탐색(`frontend/index.html#hash`) 시 데이터 로딩이 끝난 후 강제로 해당 DOM 요소로 `ScrollIntoView()` 하는 자바스크립트 로직 필수 구현 |

---

## 5. 확장성

| 항목 | 내용 |
|------|------|
| 토픽 확장 | AI 뉴스 외 다른 관심사 토픽으로 확장 가능한 구조로 설계 |
