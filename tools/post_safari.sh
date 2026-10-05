#!/bin/bash
# Post-processing after the resumed M1 Safari 17.4.1 Phase 6 sessions complete.
# Creates NEW versioned outputs; never overwrites frozen v1 outputs.
set -euo pipefail
cd /Users/saman/p1-ternary-kernel-phase0
P6=evidence/phase6-adaptive-full-inference
R=$P6/results/m1-safari17-4-1
for f in static-session1 static-session2 adaptive-session1 adaptive-session2; do [ -f "$R/$f.json" ] || { echo "missing $f"; exit 1; }; done

echo "== 1. freeze Safari"
python3 tools/freeze_phase6_environment.py --env m1-safari17-4-1 --title "M1 Safari 17.4.1" --date 2026-10-05 --notes $R/METHODOLOGY_NOTES.md
SF=$P6/m1-safari17-4-1-freeze-2026-10-05
cp -p tools/run_safari_resume.sh "$SF/" && (cd "$SF" && shasum -a 256 $(ls | grep -v SHA256SUMS | sort) > SHA256SUMS)
(cd $P6 && rm -f phase6-m1-safari17-4-1-freeze-2026-10-05.zip && zip -qr phase6-m1-safari17-4-1-freeze-2026-10-05.zip m1-safari17-4-1-freeze-2026-10-05 && shasum -a 256 phase6-m1-safari17-4-1-freeze-2026-10-05.zip)

echo "== 2. Phase 6 summary v2 (4 environments)"
python3 tools/phase6_consolidate.py --out-dir final-v2 --safari-freeze m1-safari17-4-1-freeze-2026-10-05
cp -p tools/phase6_consolidate.py tools/evaluate_phase6_environment.py $P6/final-v2/
(cd $P6/final-v2 && shasum -a 256 $(ls | grep -v SHA256SUMS | sort) > SHA256SUMS)

echo "== 3. Phase 7 v2 (4 environments)"
P7=evidence/phase7-break-even-v2; mkdir -p $P7/inputs && cp -Rp evidence/phase7-break-even/inputs/phase5d-m1 $P7/inputs/
I=$P7/inputs/phase5d-m1; H=claude-code-p1-handoff-2026-09-15
python3 tools/phase7_break_even.py \
  --env "windows-chrome152=$H/current-results/windows-chrome152/evaluation.json" \
  --env "m1-chrome153=$P6/m1-chrome153-freeze-2026-09-15/evaluation.json" \
  --env "m1-firefox155=$P6/m1-firefox155-freeze-2026-10-05/evaluation.json" \
  --env "m1-safari17-4-1=$SF/evaluation.json" \
  --phase5d "m1-chrome153=$I/mac-chrome153-run1.json,$I/mac-chrome153-run2.json" \
  --phase5d "m1-firefox155=$I/mac-firefox155-run1.json,$I/mac-firefox155-run2.json" \
  --phase5d "m1-safari17-4-1=$I/mac-safari1741-run1.json,$I/mac-safari1741-run2.json" \
  --out $P7/phase7-break-even.json
cp -p tools/phase7_break_even.py $P7/

echo "== 4. figures (SVG + LaTeX) from v2 summary"
export P6_SUMMARY=$PWD/$P6/final-v2/PHASE6_SUMMARY.json
python3 tools/make_figures.py
python3 tools/make_latex_figures.py articles/latex/article1
python3 tools/make_latex_figures.py articles/latex/article2

echo "== 5. evidence tables v2"
python3 tools/make_evidence_tables.py $P6/final-v2/PHASE6_SUMMARY.json $P7/phase7-break-even.json > /tmp/p1_tables_v2.md
echo "tables -> /tmp/p1_tables_v2.md"
