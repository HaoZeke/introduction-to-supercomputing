#!/bin/bash
set -eu
cd "$(dirname "$0")/.."
sudo docker compose --profile two-node down
