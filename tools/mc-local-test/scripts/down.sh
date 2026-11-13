#!/bin/bash
set -eu
cd "$(dirname "$0")/.."
sudo docker compose down
