#!/bin/bash
# Run the course exercises inside the login container, from the NFS home.
set -eu
cd "$(dirname "$0")/.."
sudo docker compose exec -T login1 cp /opt/mc/etc/z-01-eessi.sh /etc/profile.d/z-01-eessi.sh
sudo docker compose exec -u user01 -T login1 bash -lc 'cat > "$HOME/inside-checks.sh" && bash "$HOME/inside-checks.sh"' < scripts/inside-checks.sh
echo "===== node-local leftovers ====="
sudo docker compose exec node1 bash -c 'ls -la /localscratch || true'
sudo docker compose exec node2 bash -c 'ls -la /localscratch || true'
