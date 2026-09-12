#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
python3 -m compileall -q "$root/backend/app" "$root/backend/alembic"
python3 - "$root" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1])
bad = {"\u200c", "\u200d", "\ufeff"}
files = [*root.glob("backend/**/*.py"), *root.glob("scripts/*.py")]
found = [(path, char) for path in files for char in bad if char in path.read_text(encoding="utf-8")]
if found:
    for path, char in found:
        print(f"Forbidden hidden Unicode {ord(char):#06x} in {path}")
    raise SystemExit(1)
PY
for file in "$root"/frontend/src/*.js "$root"/frontend/sw.js; do
  node --check "$file"
done
if python3 -c 'import pytest' >/dev/null 2>&1; then
  (cd "$root/backend" && python3 -m pytest -q)
fi
printf 'Lila checks passed.\n'
