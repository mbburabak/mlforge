#!/usr/bin/env bash
# SessionStart: load ML project working memory into context.
# Silent (no output) when the project has no mlforge state — zero noise on non-ML repos.
set -euo pipefail

[ -d ml ] || [ -d experiments ] || exit 0

echo "## mlforge project state"

if [ -f ml/PROBLEM.md ]; then
  head -4 ml/PROBLEM.md | sed 's/^/  /'
fi

if [ -f ml/STACK.md ]; then
  updated=$(grep -m1 '\*\*Updated\*\*' ml/STACK.md 2>/dev/null || true)
  echo "  STACK.md present. ${updated}"
fi

if [ -f ml/gates.json ]; then
  python3 - <<'EOF' 2>/dev/null || true
import json
g = json.load(open("ml/gates.json")).get("gates", [])
if g:
    last = g[-1]
    waived = sum(1 for x in g if x.get("waived"))
    print(f"  Gates: {len(g)} recorded ({waived} waived). Last: {last.get('gate')} ({last.get('date')}, {last.get('by')})")
EOF
fi

if [ -f experiments/journal.md ]; then
  planned=$(grep -c 'Status\*\*: PLANNED' experiments/journal.md 2>/dev/null || echo 0)
  total=$(grep -c '^### ' experiments/journal.md 2>/dev/null || echo 0)
  echo "  Journal: ${total} experiments, ${planned} still open (PLANNED)."
fi

if [ -f experiments/lessons.md ]; then
  active=$(grep -c '^\- \[ACTIVE' experiments/lessons.md 2>/dev/null || echo 0)
  if [ "${active}" -gt 0 ]; then
    echo "  ACTIVE rules (apply as constraints):"
    grep '^\- \[ACTIVE' experiments/lessons.md | head -10 | sed 's/^/    /'
  fi
fi

if [ -f ml/notes/datasets.md ]; then
  echo "  Dataset notes exist (ml/notes/datasets.md) — surface before querying noted tables."
fi

exit 0
