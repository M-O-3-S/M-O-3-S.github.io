# AI News Archive (`M-O-3-S.github.io`)

로컬 환경에서 AI 뉴스를 자동 수집/요약/태깅하고, 결과를 정적 웹(`frontend/`)과 Telegram 알림으로 발행하는 프로젝트입니다.

## AI Tool Entry
- AI coding tool guide: `AGENTS.md` (primary), `CLAUDE.md`, `GEMINI.md`

## 한눈에 보기
- 수집: RSS 피드 크롤링
- 처리: Ollama 로컬 LLM 요약/태그 생성
- 발행: `frontend/data` JSON 생성 + Telegram 알림 + Git 배포
- 스케줄: Daily/Weekly 자동 실행

## 빠른 시작 (권장)
프로젝트 루트에서 아래 한 줄 실행:

```bash
./start_news_archive_scheduler.sh
```

이 스크립트는 다음을 자동으로 처리합니다.
1. `.venv` 생성 및 의존성 설치
2. `backend/config/.env` 파일 준비(`.env.example` 기반)
3. Ollama 서비스 확인 및 모델 준비
4. 스케줄러 백그라운드 실행 (`logs/scheduler.log`, `logs/scheduler.pid`)
5. macOS에서 시스템 절전 방지(`caffeinate`)

## 수동 실행 (개별 테스트)
데일리 파이프라인 1회 실행:

```bash
python3 backend/src/main.py --mode daily
```

위클리 파이프라인 1회 실행:

```bash
python3 backend/src/main.py --mode weekly
```

## 주요 설정 파일
- 스케줄/모델/RSS: `backend/config/config.yml`
- Telegram 환경변수: `backend/config/.env`
- Python 의존성: `backend/requirements.txt`

## 로그/운영
스케줄러 로그 보기:

```bash
tail -f logs/scheduler.log
```

스케줄러 중지:

```bash
kill $(cat logs/scheduler.pid)
```

## 디렉토리 구조
```text
backend/   # 크롤러/처리/발행/배포 파이프라인
docs/      # PRD, 아키텍처, 운영/UX 문서
frontend/  # 정적 웹 페이지 + 생성 데이터(JSON, DB)
tests/     # PoC/인프라 테스트 스크립트
```

## 참고
- 현재 저장소에는 기획/설계 문서와 초기 구현이 함께 포함되어 있습니다.
- 상세 요구사항: `docs/PRD_AI_News_Archive.md`, `docs/DEV_Requirements_AI_News_Archive.md`
