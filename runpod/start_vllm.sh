#!/usr/bin/env bash
# Runs ON the pod. One engine serves System 1 (LoRA jev-decision) and System 2 (base lm_head).
set -euo pipefail
pkill -f "vllm serve" || true
nohup /workspace/vllm-env/bin/vllm serve /workspace/JEV-9B --served-model-name autotrust/JEV-9B \
  --enable-lora --max-lora-rank 32 --lora-modules jev-decision=/workspace/JEV-9B/adapter_vllm \
  --logprobs-mode processed_logprobs --max-model-len 32768 --gpu-memory-utilization 0.90 \
  --host 127.0.0.1 --port 8000 > /workspace/vllm.log 2>&1 &
for i in $(seq 1 120); do
  curl -sf http://127.0.0.1:8000/v1/models >/dev/null && { echo "vllm ready after ${i}0s"; exit 0; }
  sleep 10
done
echo "vllm did not start"; tail -50 /workspace/vllm.log; exit 1
