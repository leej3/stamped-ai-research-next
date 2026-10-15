#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

run_id="$(date -u +%Y%m%dT%H%M%SZ)"
code_revision="$(git rev-parse HEAD)"
log_prefix="logs/${run_id}-analysis-"
working_tree_state="clean"
if [[ -n "$(git status --porcelain)" ]]; then
  working_tree_state="dirty"
fi

pixi run duct --output-prefix "$log_prefix" --fail-time 0 \
  --message "Group analysis; code=${code_revision}" \
  pixi run analysis

pixi run python scripts/write_run_record.py \
  --run-id "$run_id" \
  --code-revision "$code_revision" \
  --working-tree-state "$working_tree_state" \
  --log-prefix "$log_prefix"
