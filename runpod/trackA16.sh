#!/usr/bin/env bash
# Track A continued at concurrency 16 after the in-flight ANLI run (PID passed as $1) finishes by itself.
cd /workspace/jev
set -a; source /root/.jev_secrets.env; set +a
export JEVSTUDY_ROOT=/workspace/jev GPU_USD_PER_HR=0.59
J=/root/venv-client/bin/jevstudy
LIMIT=300
stamp() { echo "{\"track\":\"$1\",\"panel\":\"$2\",\"event\":\"$3\",\"t\":$(date +%s)}" >> results/gpu_windows.jsonl; }
while kill -0 "$1" 2>/dev/null; do sleep 15; done
stamp A anli_final end
# rerun anli once more through the cache so any rows lost in a crash are filled (cache hits cost nothing)
$J run --panel anli_final --systems jev-s1,astra,fable --concurrency 16 --stage-forecast $LIMIT || exit 1
for p in controlled_final judgebench_final banking_final folio_final_rev controlled_final_rev; do
  stamp A $p start
  $J run --panel $p --systems jev-s1,astra,fable --concurrency 16 --stage-forecast $LIMIT || { echo "TRACK A STOPPED at $p"; exit 1; }
  stamp A $p end
done
$J run --panel folio_final --systems astra-max,fable-max --concurrency 16 --run-name effortmax --stage-forecast $LIMIT || exit 1
$J run --panel controlled_final --systems astra-max,fable-max --ids @manifests/controlled_base_ids.json --concurrency 16 --run-name effortmax --stage-forecast $LIMIT || exit 1
echo "TRACK A DONE"
