#!/usr/bin/env bash
# A6: S1 reversal passes, then S2 in full on controlled_final, and on harness-escalated items elsewhere.
cd /workspace/jev
set -a; source /root/.jev_secrets.env; set +a
export JEVSTUDY_ROOT=/workspace/jev GPU_USD_PER_HR=0.59
J=/root/venv-client/bin/jevstudy
PY=/root/venv-client/bin/python
stamp() { echo "{\"track\":\"$1\",\"panel\":\"$2\",\"event\":\"$3\",\"t\":$(date +%s)}" >> results/gpu_windows.jsonl; }
for p in halueval_rev anli_final_rev judgebench_final_rev controlled_deep_rev controlled_final_ctlrev folio_final_rev controlled_final_rev; do
  $J run --panel $p --systems jev-s1 --concurrency 8 || echo "S1 issue $p"
done
$J run --panel rewardbench_rev --systems jev-s1 --ids @manifests/rewardbench_500_rev.json --concurrency 8
$PY -m jevstudy.harness --root . --escalated anli_final
$PY -m jevstudy.harness --root . --escalated judgebench_final --ids manifests/judgebench_partial.json
$PY -m jevstudy.harness --root . --escalated rewardbench --ids manifests/rewardbench_500.json
$PY -m jevstudy.harness --root . --escalated halueval
stamp B controlled_final start; $J run --panel controlled_final --systems jev-s2 --concurrency 96; stamp B controlled_final end
for p in anli_final judgebench_final rewardbench halueval; do
  stamp B $p-escalated start; $J run --panel $p --systems jev-s2 --ids @manifests/escalated_$p.json --concurrency 96; stamp B $p-escalated end
done
echo "GPU LEAN2 DONE"
