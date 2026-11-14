#!/bin/bash
set -eu
cd "$(dirname "$0")/.."

if [ ! -s secrets/munge.key ]; then
    mkdir -p secrets
    dd if=/dev/urandom of=secrets/munge.key bs=1 count=1024 status=none
    chmod 400 secrets/munge.key
fi

# Docker's nftables rules do not match the legacy filter table. A legacy
# FORWARD policy of DROP blackholes traffic on compose bridges.
if command -v iptables-legacy >/dev/null 2>&1; then
    if sudo iptables-legacy -S FORWARD 2>/dev/null | head -n 1 | grep -q -- '-P FORWARD DROP'; then
        sudo iptables-legacy -P FORWARD ACCEPT
    fi
fi

# MC_NODES=1 leaves node2 out. Slurm still lists it, so it stays down.
compose=(sudo docker compose)
if [ "${MC_NODES:-2}" != 1 ]; then
    compose+=(--profile two-node)
fi
up=(up -d)
if [ "${MC_SKIP_BUILD:-0}" != 1 ]; then
    up+=(--build)
fi
"${compose[@]}" "${up[@]}"
"${compose[@]}" ps
