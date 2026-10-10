#!/usr/bin/env bash
# GPU-only work (no API spend): JEV-9B S1 on harness reversal panels and the judge track, then S2 on the judge track.
cd /workspace/jev
set -a; source /root/.jev_secrets.env; set +a
export JEVSTUDY_ROOT=/workspace/jev GPU_USD_PER_HR=0.59
J=/root/venv-client/bin/jevstudy
stamp() { echo "{\"track\":\"$1\",\"panel\":\"$2\",\"event\":\"$3\",\"t\":$(date +%s)}" >> results/gpu_windows.jsonl; }
for p in rewardbench halueval rewardbench_rev halueval_rev anli_final_rev judgebench_final_rev banking_final_rev controlled_deep_rev controlled_final_ctlrev folio_final_rev controlled_final_rev; do
  $J run --panel $p --systems jev-s1 --concurrency 8 || echo "S1 issue $p"
done
for p in rewardbench halueval; do
  stamp B $p start; $J run --panel $p --systems jev-s2 --concurrency 64 || echo "S2 issue $p"; stamp B $p end
done
echo "GPU ONLY DONE"
