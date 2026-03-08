#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
LOG_DIR="$ROOT_DIR/logs"
SCHEDULER_LOG="$LOG_DIR/scheduler.log"
SCHEDULER_PID_FILE="$LOG_DIR/scheduler.pid"
OLLAMA_LOG="$LOG_DIR/ollama.log"
OLLAMA_PID_FILE="$LOG_DIR/ollama.pid"
REQUIREMENTS_FILE="$ROOT_DIR/backend/requirements.txt"
ENV_FILE="$ROOT_DIR/backend/config/.env"
ENV_EXAMPLE_FILE="$ROOT_DIR/backend/config/.env.example"
CONFIG_FILE="$ROOT_DIR/backend/config/config.yml"

mkdir -p "$LOG_DIR"

if [[ -f "$SCHEDULER_PID_FILE" ]]; then
  OLD_PID="$(cat "$SCHEDULER_PID_FILE" 2>/dev/null || true)"
  if [[ -n "${OLD_PID:-}" ]] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "Scheduler is already running. PID=$OLD_PID"
    echo "Log: $SCHEDULER_LOG"
    exit 0
  fi
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but not found."
  exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "[1/6] Creating virtual environment at .venv"
  python3 -m venv "$VENV_DIR"
fi

VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

echo "[2/6] Ensuring Python dependencies"
"$VENV_PYTHON" -c "import requests, feedparser, schedule, dotenv, yaml" >/dev/null 2>&1 || \
  "$VENV_PIP" install -r "$REQUIREMENTS_FILE"

if [[ ! -f "$ENV_FILE" ]]; then
  if [[ -f "$ENV_EXAMPLE_FILE" ]]; then
    cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
    echo "[3/6] Created backend/config/.env from .env.example"
    echo "      Please edit $ENV_FILE if you want Telegram alerts."
  else
    echo "[3/6] Warning: .env.example not found. Telegram alerts may be skipped."
  fi
else
  echo "[3/6] .env exists"
fi

MODEL_NAME="$("$VENV_PYTHON" -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE','r',encoding='utf-8')) or {}; print((c.get('system') or {}).get('llm_model','gemma3:4b'))")"
echo "[4/6] Target Ollama model: $MODEL_NAME"

if command -v ollama >/dev/null 2>&1; then
  if ! curl -fsS "http://127.0.0.1:11434/api/tags" >/dev/null 2>&1; then
    echo "      Starting Ollama service..."
    nohup ollama serve > "$OLLAMA_LOG" 2>&1 &
    OLLAMA_PID=$!
    echo "$OLLAMA_PID" > "$OLLAMA_PID_FILE"
    sleep 2
  fi

  if ! ollama list 2>/dev/null | awk '{print $1}' | grep -Fxq "$MODEL_NAME"; then
    echo "      Pulling missing model: $MODEL_NAME"
    ollama pull "$MODEL_NAME"
  fi
else
  echo "      Warning: ollama command not found. AI summarization may fail."
fi

echo "[5/6] Starting scheduler in background"
nohup "$VENV_PYTHON" "$ROOT_DIR/backend/src/scheduler.py" > "$SCHEDULER_LOG" 2>&1 &
SCHEDULER_PID=$!
echo "$SCHEDULER_PID" > "$SCHEDULER_PID_FILE"

if command -v caffeinate >/dev/null 2>&1; then
  echo "[6/6] Enabling caffeinate to prevent system sleep while scheduler is alive"
  nohup caffeinate -imsu -w "$SCHEDULER_PID" >/dev/null 2>&1 &
fi

echo
echo "Scheduler started."
echo "PID: $SCHEDULER_PID"
echo "Log: $SCHEDULER_LOG"
echo
echo "Check status:"
echo "  tail -f $SCHEDULER_LOG"
echo
echo "Stop scheduler:"
echo "  kill \$(cat $SCHEDULER_PID_FILE)"
