#!/usr/bin/env bash
# Resume paid synchronous work after the credit top-up (cache supplies everything already answered).
cd /workspace/jev
set -a; source /root/.jev_secrets.env; set +a
export JEVSTUDY_ROOT=/workspace/jev GPU_USD_PER_HR=0.59
J=/root/venv-client/bin/jevstudy
LIMIT=250
stamp() { echo "{\"track\":\"$1\",\"panel\":\"$2\",\"event\":\"$3\",\"t\":$(date +%s)}" >> results/gpu_windows.jsonl; }
for p in judgebench_final folio_final_rev controlled_final_rev; do
  stamp A $p start
  $J run --panel $p --systems jev-s1,astra,fable --concurrency 16 --stage-forecast $LIMIT || { echo "STOPPED at $p"; exit 1; }
  stamp A $p end
done
$J run --panel folio_final --systems astra-max,fable-max --concurrency 16 --run-name effortmax --stage-forecast $LIMIT || exit 1
$J run --panel controlled_final --systems astra-max,fable-max --ids @manifests/controlled_base_ids.json --concurrency 16 --run-name effortmax --stage-forecast $LIMIT || exit 1
echo "RESUME SYNC DONE"
