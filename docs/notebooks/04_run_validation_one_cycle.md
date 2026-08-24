# sftools/run_validation.py (Step 4.1, One Cycle)

Writes, under `--out`:

- `validation_report.json` / `.txt` — the GODAE scorecard for
  temp/ssh/salt/speed, the Section 9.3 pass/fail criteria, numerical-
  stability check, and (if `--insitu-files` was given) the in-situ
  scorecard.
- `taylor_diagram.png` — combined Taylor diagram, all scored variables
  (skip with `--no-plots`).

In-situ scoring is **informational only** by default — a cycle with no
matching obs still passes/fails purely on the Section 9.3 grid criteria.
Add `--require-insitu-pass` to also gate `all_pass` on an in-situ
surface-temperature check (note: this uses a separate, deliberately
looser ±1.0 degC tolerance, not a Section 9.3 number — point-obs bias and
gridded-product RMSE aren't the same statistic).

Exit code: `0` = all criteria passed, `1` = at least one failed (reports
still written), `2` = validation itself couldn't run (missing/corrupt
input — no reports written).

```bash
python -m sftools.run_validation \
    --croco-his forecast/model-runs/Canary_12/20260714/fcst/CROCO_FILES/croco_his.nc \
    --reference forecast/model-runs/Canary_12/20260714/downloaded_data/MERCATOR/MERCATOR_20260714_00.nc \
    --out forecast/model-runs/Canary_12/20260714/fcst/validation \
    --yorig 2000 --region Canary_12 --cycle-tag 20260714

# also score against in-situ obs, and require them to pass too:
python -m sftools.run_validation --croco-his ... --reference ... --out ... \
    --insitu-files "downloaded_data/INSITU/2026-07-1*.nc" --require-insitu-pass
```
