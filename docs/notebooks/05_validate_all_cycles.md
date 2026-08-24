# forecast/validate_all_cycles.sh (Batch, Every Cycle)

Finds every cycle directory under `forecast/model-runs/<REGION>/` (or every
region if `--region` is omitted), skips any that already has a
`validation_report.json` (unless `--force`), and calls `run_validation.py`
on the rest. Appends one row per cycle to a running `validation_summary.csv`
per region — this is what `02_validation.ipynb` Section 8 loads to plot
criteria trends across cycles. Handles both existing cycle-directory naming
conventions in this repo (`run_forecast_today.sh`'s plain `YYYYMMDD`, and
the AGRIF matrix driver `run_forecast_cycle.sh`'s suffixed
`YYYYMMDD_plain`-style names). One bad cycle never aborts the batch; a
timestamped log goes to `forecast/logs/`.

```bash
cd forecast
./validate_all_cycles.sh                      # every region, every cycle
./validate_all_cycles.sh --region Canary_12    # one region only
./validate_all_cycles.sh --since 20260701      # skip cycles before this date
./validate_all_cycles.sh --force               # re-validate everything
./validate_all_cycles.sh --dry-run             # show what WOULD run, do nothing
./validate_all_cycles.sh --phase hcast --root ../hindcast/model-runs
                                                # same script, hindcast tree
./validate_all_cycles.sh --insitu-files "../hindcast/downloaded_data/INSITU/*.nc"
                                                # also score every cycle against in-situ obs
                                                # (add --require-insitu-pass to gate on it too)
```
