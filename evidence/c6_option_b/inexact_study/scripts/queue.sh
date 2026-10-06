#!/bin/bash
# Runs the inexact-impact worlds. One world at a time while the 0g v5 run (s4_v5.py) is alive;
# an exact/inexact pair launched together once it has exited.
W=/private/tmp/claude-501/-Users-new-RiderProjects-ai-RPG-test/266628b5-c225-443d-b8f6-8f99d66d38db/scratchpad/inexact_study
PY=/Users/new/RiderProjects/ai_RPG_test/.venv/bin/python
run(){ # engine entropy world
  out=$W/runs/$1_$2_$3
  [ -f $out/COSTS.json ] && return 0
  rm -rf $out
  echo "$(date '+%F %T') start $1 $2 $3 load $(sysctl -n vm.loadavg)" >> $W/queue.log
  (cd $W/repo_$1 && $PY tools/c6_option_b_check.py --backend native --parallel --entropy $2 --world $3 --output $out > $W/runs/$1_$2_$3.log 2>&1); rc=$?
  echo "$(date '+%F %T') end $1 $2 $3 rc $rc load $(sysctl -n vm.loadavg)" >> $W/queue.log
}
v5(){ pgrep -f s4_v5.py >/dev/null; }
pair(){ # entropy world: both engines
  if v5; then run exact $1 $2; run inexact $1 $2
  else run exact $1 $2 & run inexact $1 $2 & wait; fi
}
run exact smoke 1
[ -f $W/runs/exact_smoke_1/COSTS.json ] || { echo "$(date '+%F %T') STOP: exact smoke 1 failed" >> $W/queue.log; exit 1; }
for w in 2 3 4 5 6 7; do pair development $w; done
run inexact smoke 0; run inexact smoke 1; run inexact development 0; run inexact development 1
echo "$(date '+%F %T') QUEUE DONE" >> $W/queue.log
