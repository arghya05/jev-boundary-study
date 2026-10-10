#!/usr/bin/env bash
# Runs ON the RunPod pod. Installs the client package and vLLM, downloads JEV-9B, starts the server.
set -euo pipefail
cd /workspace/jev
export PATH="$HOME/.local/bin:$PATH"
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
set -a; source /root/.jev_secrets.env; set +a          # API keys live only here (chmod 600), never in the repo
JEV_REV=b63f651ce8ed64481d3f5e73ecdb05f740042f01

# client environment
[ -d .venv ] || uv venv -q -p 3.12 .venv
uv pip install -q -p .venv/bin/python -e '.[test]'
# vLLM in its own environment so the client lock stays small
[ -d /workspace/vllm-env ] || uv venv -q -p 3.12 /workspace/vllm-env
uv pip install -q -p /workspace/vllm-env/bin/python "vllm==0.31.0" huggingface_hub
/workspace/vllm-env/bin/hf download autotrust/JEV-9B --revision "$JEV_REV" --local-dir /workspace/JEV-9B >/dev/null
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
echo "setup done"
