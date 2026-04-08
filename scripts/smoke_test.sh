#!/usr/bin/env bash
set -euo pipefail

python3 -m unittest tests/test_refresh_smoke.py

git ls-files | rg '\\.DS_Store$' >/dev/null && {
  echo "Tracked .DS_Store file found"
  exit 1
} || true

[[ -f docs/roadmap.md ]]
[[ -f docs/skills-playbook.md ]]
[[ -f SKILLS_PLAYBOOK.md ]]
[[ -d skills ]]

python3 -m py_compile refresh_dashboard.py

echo "smoke_test.sh: OK"
