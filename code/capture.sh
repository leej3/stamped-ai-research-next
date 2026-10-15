#!/bin/sh
set -eu
mkdir -p logs/paired results
export MPLCONFIGDIR="${TMPDIR:-/tmp}/stamped-paired-mpl"
export DUCT_CONFIG_PATHS=/dev/null
set +e
duct --output-prefix logs/paired/run_ --fail-time 0 --sample-interval 1 \
  --report-interval 1 --capture-outputs all --record-types all \
  --message 'paired-v1: synthetic paired mean and t interval' \
  python code/compute.py > logs/paired/outer-summary.txt 2>&1
status=$?
set -e
cat logs/paired/outer-summary.txt
exit "$status"
