#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: scripts/bump-version.sh <version>" >&2
  exit 1
fi

version="$1"

python3 - "$version" <<'PY'
import json
import sys
from pathlib import Path

version = sys.argv[1]
config = json.loads(Path(".version-bump.json").read_text())

for item in config["files"]:
    path = Path(item["path"])
    data = json.loads(path.read_text())
    target = data
    parts = item["field"].split(".")
    for part in parts[:-1]:
        target = target[int(part)] if part.isdigit() else target[part]
    last = parts[-1]
    if last.isdigit():
        target[int(last)] = version
    else:
        target[last] = version
    path.write_text(json.dumps(data, indent=2) + "\n")
PY
