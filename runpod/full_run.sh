#!/usr/bin/env bash
# Full preregistered run (research/PREREGISTRATION.md). Runs ON the pod under nohup.
set -uo pipefail
cd /workspace/jev
set -a; source /root/.jev_secrets.env; set +a
export JEVSTUDY_ROOT=/workspace/jev GPU_USD_PER_HR=0.59
J=/root/venv-client/bin/jevstudy
LIMIT=300   # = ~1.5x conservative forecast incl. spend so far; review trigger, not a target
stamp() { echo "{\"track\":\"$1\",\"panel\":\"$2\",\"event\":\"$3\",\"t\":$(date +%s)}" >> results/gpu_windows.jsonl; }
python3 -c "import json; ids=[json.loads(l)['task_id'] for l in open('data/panels/controlled_final.tasks.jsonl') if json.loads(l)['meta']['condition']=='base']; json.dump({'ids':ids},open('manifests/controlled_base_ids.json','w'))"

trackA() {
  for p in folio_final anli_final controlled_final judgebench_final banking_final folio_final_rev controlled_final_rev; do
    stamp A $p start
    $J run --panel $p --systems jev-s1,astra,fable --concurrency 6 --stage-forecast $LIMIT || { echo "TRACK A STOPPED at $p"; return 1; }
    stamp A $p end
  done
  $J run --panel folio_final --systems astra-max,fable-max --concurrency 6 --run-name effortmax --stage-forecast $LIMIT || return 1
  $J run --panel controlled_final --systems astra-max,fable-max --ids @manifests/controlled_base_ids.json --concurrency 6 --run-name effortmax --stage-forecast $LIMIT || return 1
  echo "TRACK A DONE"
}
trackB() {
  for p in folio_final anli_final controlled_final judgebench_final banking_final folio_final_rev controlled_final_rev dev_pilot; do
    stamp B $p start
    $J run --panel $p --systems jev-s2 --concurrency 32 || echo "S2 issue on $p"
    stamp B $p end
  done
  echo "TRACK B DONE"
}
trackA > /root/trackA.log 2>&1 &
PA=$!
trackB > /root/trackB.log 2>&1 &
PB=$!
wait $PA; wait $PB
# latency track last, with nothing else running: fresh calls, concurrency 1, interleaved providers
stamp L folio_latency start
$J run --panel folio_final --systems jev-s1,astra,fable --ids @manifests/latency_subset.json --fresh --run-name latency --concurrency 1 --stage-forecast $LIMIT > /root/latency.log 2>&1
stamp L folio_latency end
echo "ALL DONE $(date)" >> /root/trackA.log
