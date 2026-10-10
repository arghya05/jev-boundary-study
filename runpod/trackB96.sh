#!/usr/bin/env bash
# System-2 track restarted at concurrency 96 (GPU-bound; completed items come from cache).
cd /workspace/jev
set -a; source /root/.jev_secrets.env; set +a
export JEVSTUDY_ROOT=/workspace/jev GPU_USD_PER_HR=0.59
J=/root/venv-client/bin/jevstudy
stamp() { echo "{\"track\":\"$1\",\"panel\":\"$2\",\"event\":\"$3\",\"t\":$(date +%s)}" >> results/gpu_windows.jsonl; }
for p in folio_final anli_final controlled_final judgebench_final banking_final folio_final_rev controlled_final_rev; do
  stamp B $p start
  $J run --panel $p --systems jev-s2 --concurrency 96 || echo "S2 issue on $p"
  stamp B $p end
done
echo "TRACK B DONE"
