#!/bin/bash
# Exact reference world for each inexact world, then impact.py per world and summarize.py.
W=$(cd "$(dirname "$0")" && pwd); R=/Users/new/RiderProjects/ai_RPG_test; E=$R/evidence/c6_option_b; PY=$R/.venv/bin/python
mkdir -p $W/results
ref(){ case $1 in
  smoke_0) echo $E/reference_smoke_0/world.json.gz;;
  smoke_1) echo $W/runs/exact_smoke_1/world.json.gz;;
  development_0) echo $E/audited_v3_development_0/world.json.gz;;
  development_1) echo $E/quiet_session_20261006_161801/worlds/reference_development_1/world.json.gz;;
  *) echo $W/runs/exact_$1/world.json.gz;; esac; }
for w in smoke_0 smoke_1 development_0 development_1 development_2 development_3 development_4 development_5 development_6 development_7; do
  $PY $W/impact.py $(ref $w) $W/runs/inexact_$w/world.json.gz $W/results/$w.json > /dev/null || echo "FAIL $w"
done
$PY $W/summarize.py
