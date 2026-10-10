#!/usr/bin/env bash
# Local helper: create / sync / ssh / stop / delete the study pod. Usage: runpod/pod.sh <cmd>
set -euo pipefail
KEY=~/.runpod/ssh/runpodctl-ssh-key
STATE=runpod/.pod_id
GPU="${GPU:-NVIDIA A40}"
IMAGE="runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04"
pod_id() { cat "$STATE"; }
ssh_target() {
  runpodctl ssh info "$(pod_id)" -o json | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("ip") or d["publicIp"], d.get("port") or d["sshPort"])'
}
case "$1" in
  create)
    runpodctl pod create --name jevstudy --gpu-id "$GPU" --gpu-count 1 --cloud-type SECURE --image "$IMAGE" \
      --container-disk-in-gb 60 --ports '8888/http,22/tcp' --wait -o json > runpod/.pod_create.json
    grep -o '"id": *"[a-z0-9]*"' runpod/.pod_create.json | head -1 | sed 's/.*"\([a-z0-9]*\)"$/\1/' > "$STATE"
    echo "pod $(pod_id)";;
  info) runpodctl ssh info "$(pod_id)";;
  ssh) read -r IP PORT < <(ssh_target); ssh -i $KEY -o StrictHostKeyChecking=accept-new -p "$PORT" root@"$IP" "${@:2}";;
  sync)
    read -r IP PORT < <(ssh_target)
    rsync -rlptz --no-owner --no-group --delete --exclude __pycache__ --exclude .pytest_cache -e "ssh -i $KEY -o StrictHostKeyChecking=accept-new -p $PORT" \
      --exclude .venv --exclude .git --exclude 'results/cache' --exclude 'data/raw' --exclude 'runpod/.pod*' \
      ./ root@"$IP":/workspace/jev/;;
  pull)
    read -r IP PORT < <(ssh_target)
    rsync -rlptz -e "ssh -i $KEY -p $PORT" root@"$IP":/workspace/jev/results/ ./results/
    rsync -rlptz -e "ssh -i $KEY -p $PORT" root@"$IP":/workspace/jev/manifests/ ./manifests/
    rsync -rlptz -e "ssh -i $KEY -p $PORT" --include '*/' --include '*.jsonl' --exclude '*' root@"$IP":/workspace/jev/data/panels/ ./data/panels/;;
  secrets)
    # write API keys to the pod (mode 600) without echoing them
    read -r IP PORT < <(ssh_target)
    { printf 'OPENAI_API_KEY=%s\n' "$OPENAI_API_KEY"; printf 'ANTHROPIC_API_KEY=%s\n' "$ANTHROPIC_API_KEY"; printf 'HF_TOKEN=%s\n' "$HF_TOKEN"; } \
      | ssh -i $KEY -p "$PORT" root@"$IP" 'umask 077; cat > /root/.jev_secrets.env';;
  stop) runpodctl stop pod "$(pod_id)";;
  start) runpodctl start pod "$(pod_id)";;
  delete) runpodctl remove pod "$(pod_id)" && rm -f "$STATE";;
  *) echo "usage: $0 create|info|ssh|sync|pull|secrets|stop|start|delete"; exit 1;;
esac
