#!/usr/bin/env bash
set -euo pipefail
REV=b63f651ce8ed64481d3f5e73ecdb05f740042f01
MODEL_DIR=${MODEL_DIR:-/models/JEV-9B}
[ -f "$MODEL_DIR/config.json" ] || hf download autotrust/JEV-9B --revision "$REV" --local-dir "$MODEL_DIR"
vllm serve "$MODEL_DIR" --served-model-name autotrust/JEV-9B --enable-lora --max-lora-rank 32 \
  --lora-modules jev-decision="$MODEL_DIR/adapter_vllm" --logprobs-mode processed_logprobs \
  --max-model-len "${MAX_MODEL_LEN:-32768}" --host 127.0.0.1 --port 8000 &
until curl -sf http://127.0.0.1:8000/v1/models >/dev/null; do sleep 5; done
exec uvicorn jevstudy.server:app --host 0.0.0.0 --port 8080
