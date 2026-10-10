#!/usr/bin/env bash
# Lean GPU queue (A5): S1 reversal panels needed by JEV-H, then S2 only on the reduced scope.
cd /workspace/jev
set -a; source /root/.jev_secrets.env; set +a
export JEVSTUDY_ROOT=/workspace/jev GPU_USD_PER_HR=0.59
J=/root/venv-client/bin/jevstudy
stamp() { echo "{\"track\":\"$1\",\"panel\":\"$2\",\"event\":\"$3\",\"t\":$(date +%s)}" >> results/gpu_windows.jsonl; }
while pgrep -f "panel anli_final --systems jev-s2" >/dev/null || pgrep -f "systems jev-s1 --concurrency 8" >/dev/null; do sleep 20; done
for p in halueval_rev anli_final_rev judgebench_final_rev controlled_deep_rev controlled_final_ctlrev folio_final_rev controlled_final_rev; do
  $J run --panel $p --systems jev-s1 --concurrency 8 || echo "S1 issue $p"
done
$J run --panel rewardbench_rev --systems jev-s1 --ids @manifests/rewardbench_500_rev.json --concurrency 8
stamp B controlled_final start; $J run --panel controlled_final --systems jev-s2 --concurrency 96; stamp B controlled_final end
stamp B rewardbench start; $J run --panel rewardbench --systems jev-s2 --ids @manifests/rewardbench_500.json --concurrency 96; stamp B rewardbench end
stamp B halueval start; $J run --panel halueval --systems jev-s2 --concurrency 96; stamp B halueval end
stamp B judgebench_final start; $J run --panel judgebench_final --systems jev-s2 --ids @manifests/judgebench_partial.json --concurrency 64; stamp B judgebench_final end
echo "GPU LEAN DONE"
