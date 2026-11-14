#!/bin/bash
# Run the course exercises inside the login container, from the NFS home.
# MC_SCOPE=all (default) runs every exercise, including the 1000-file transfer.
# MC_SCOPE=ci skips that transfer. MC_NODES=1 skips the node2 leftover check.
set -u
cd "$(dirname "$0")/.." || exit 1
scope=${MC_SCOPE:-all}
rc=0

sudo docker compose exec -T login1 cp /opt/mc/etc/z-01-eessi.sh /etc/profile.d/z-01-eessi.sh
sudo docker compose exec -u user01 -T login1 bash -c 'cat > "$HOME/extract-sbatch.py"' < scripts/extract-sbatch.py
sudo docker compose exec -u user01 -T -e MC_SCOPE="$scope" login1 \
    bash -lc 'cat > "$HOME/inside-checks.sh" && bash "$HOME/inside-checks.sh"' < scripts/inside-checks.sh \
    || rc=$?

echo "===== node-local leftovers ====="
nodes=(node1)
if [ "${MC_NODES:-2}" != 1 ]; then
    nodes+=(node2)
fi
for node in "${nodes[@]}"; do
    if ! extra=$(sudo docker compose exec "$node" bash -c 'find /localscratch -mindepth 1 -print'); then
        echo "cannot inspect /localscratch on $node"
        rc=1
        continue
    fi
    if [ -n "$extra" ]; then
        echo "leftovers on $node:"
        printf '%s\n' "$extra"
        rc=1
    else
        echo "$node /localscratch empty"
    fi
done

if [ "$rc" -ne 0 ]; then
    echo "run-checks failed"
    exit "$rc"
fi
echo "run-checks passed"
