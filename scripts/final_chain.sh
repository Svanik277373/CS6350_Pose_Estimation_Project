#!/usr/bin/env bash
# Runs the remaining report jobs one after another (CPU only), after the region tuning ends:
#   pick_rule -> auto_eval2 (re-score + agreement) -> report_figures (example cases) -> euler_track
#   bash scripts/final_chain.sh > logs/final_chain.log 2>&1
cd "$(dirname "$0")/.."
PY=venv/Scripts/python.exe
export PYTHONWARNINGS=ignore
while [ ! -f results/region_tune/summary.md ]; do sleep 30; done
echo "== pick rule"; $PY -u scripts/pick_rule.py || exit 1
echo "== re-score test pairs"; $PY -u scripts/auto_eval2.py || exit 1
echo "== example cases"; CASES=$($PY scripts/pick_cases.py); echo "$CASES"
$PY -u scripts/report_figures.py $CASES || echo "report_figures failed"
echo "== euler track"; $PY -u scripts/euler_track.py --sequence struct_near --gap 20 --pairs 40 || echo "euler_track failed"
echo "== all done"
