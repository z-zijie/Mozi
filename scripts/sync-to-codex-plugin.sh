#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: scripts/sync-to-codex-plugin.sh <destination-directory>" >&2
  exit 1
fi

dest="$1"
mkdir -p "$dest"

rsync -a --delete \
  --exclude '.git/' \
  --exclude '.venv/' \
  --exclude 'node_modules/' \
  --exclude 'tmp/' \
  ./ "$dest"/
