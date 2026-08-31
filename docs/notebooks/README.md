# notebooks/ — SEA-FORWARD Jupyter Notebook Toolkit

Guided, interactive counterparts to the automated pipeline (Steps 1-5 of the
operational workflow, `sftools.cli` / `sftools/run_validation.py`). Owned by
Python Dev 1/2, DCC processes **V1** (validation) and **D1** (downstream
exercises, sensitivity analysis, animation).

```
notebooks/
├── 01_visualisation.ipynb   ← maps, sections, animations (not in this package)
├── 02_validation.ipynb      ← bias maps, scatter plots, Taylor diagrams, time
│                               series, optional in-situ scoring, batch history (V1)
├── 03_exercises.ipynb       ← guided exercises: upwelling, MLD, coastal jet, eddies (D1)
├── 04_sensitivity.ipynb     ← wind-forcing sensitivity study, Step 5.3 (U2 -> C1 -> D1)
├── 05_animation.ipynb       ← SSH+eddies, currents, scalar fields, particle
│                               advection (D1, needs py-eddy-tracker)
├── _demo_data.py            ← shared helper, NOT a notebook — see below
└── region_cells.py          ← region-picker helper cells

sftools/
├── validation.py                 ← grid-level CROCO-vs-reference comparisons (class 1/2)
├── validation_godae.py           ← GODAE OceanView scorecard + optional in-situ (class 4)
├── animate.py                    ← SSH/eddy, current, scalar, particle animations
└── run_validation.py             ← validates ONE cycle (Step 4.1) -- see below

forecast/
├── validate_all_cycles.sh           ← validates EVERY not-yet-validated cycle
└── install_validation_crontab.sh    ← schedules validate_all_cycles.sh via cron

validation/
└── test_sftools_animate_validation.py   ← pytest suite for validation_godae.py / animate.py
```

**A note on that last change:** `validation_godae.py` and `animate.py` used
to also have stale duplicate copies under `validation/` (left over from
early development, before they were finalised) — those have been removed.
`sftools/` is now the single source of truth for every importable module;
`validation/` holds only the test suite.

## Before you start

1. **Activate the `seaforward` conda environment** and make sure `sftools` is
   installed editable from the repo root (`pip install --no-deps -e .` — see
   `sftools/README.md`). If `import sftools...` fails inside a notebook,
   this step was skipped.
2. **Launch Jupyter from the repository root**, not from inside `notebooks/`:
   ```bash
   cd seaforward        # repo root
   jupyter lab
   ```
   Every notebook does `sys.path.insert(0, "..")` to resolve `import
   sftools`, which assumes the notebook's own working directory is
   `notebooks/` and the repo root is exactly one level up. Launching from
   inside `notebooks/` itself (`cd notebooks && jupyter lab`) also works —
   what *doesn't* work is launching from anywhere else and browsing in, since
   Jupyter's working directory (not the file's location) is what `..`
   resolves against.
3. Run notebooks **in numeric order** (02 before 03 before 04) the first
   time — later notebooks reuse conventions (the reference coastal point,
   the Bakun index) introduced earlier, and 04 explicitly assumes you've
   seen 03's Exercise 1. `05_animation.ipynb` is independent of 03/04 and
   can be run any time after 02, but needs **py-eddy-tracker** installed
   (`pip install pyEddyTracker`, already in `environment.yml`) — see that
   notebook's own header cell if the import fails.

## Demo data — read this if a notebook complains about missing files

`_demo_data.py` is a shared helper (not a notebook) that every notebook
imports as `import _demo_data`. On first run, each notebook calls
`_demo_data.get_paths()` (02/03/05) or `_demo_data.get_sensitivity_paths()`
(04), which:

- looks for real data at the paths configured near the top of
  `_demo_data.py` (`SEAFORWARD_CROCO_HIS`, `SEAFORWARD_GLORYS` environment
  variables, or the hard-coded defaults pointing into `../hindcast/`);
- if not found, **auto-generates a small synthetic stand-in** (a fake
  CROCO history file with an idealised coastal-upwelling signature, a fake
  GLORYS-like reference, a fake wind field) under `notebooks/_demo_cache/`,
  and reuses it on subsequent runs.

Every notebook prints a loud `!! DEMO DATA !!` banner whenever this
fallback is active. **Treat any numbers or pass/fail results from a demo
run as illustrative only** — they exist so the toolkit can be graded/tested
before the real D10.2 (Forcing Data Archive) / D10.3 (Reference Results
Dataset) are downloaded from Zenodo, not as a substitute for real
validation.

To force a clean rebuild of the demo cache after editing `_demo_data.py`,
delete `notebooks/_demo_cache/` and re-run.

To point a notebook at your own real run instead of the defaults, either
edit the paths directly in that notebook's setup cell, or set the
environment variables before launching Jupyter:

```bash
export SEAFORWARD_CROCO_HIS=../hindcast/model-runs/Canary_12/20251225/hcast/CROCO_FILES/croco_his.nc
export SEAFORWARD_GLORYS=../hindcast/downloaded_data/GLORYS/2025_12.nc
jupyter lab
```

## Validation: one engine, three ways to run it

`sftools.validation_godae` -- the GODAE OceanView scorecard (bias, RMSD,
unbiased RMSD, correlation, two scatter-index variants, std-ratio) plus
optional class-4 in-situ scoring per depth layer -- is now the **single
statistics engine** behind every validation surface in this repo:

```
sftools.validation_godae.godae_scorecard_croco_vs_glorys()   <- grid vs reference, one variable
sftools.validation_godae.validate_against_insitu()           <- grid vs CMEMS in-situ TAC, per depth layer
```

...used identically by:

1. **`02_validation.ipynb`** (interactive, Sections 4-7) — builds the same
   scorecard, draws the Taylor diagram, and (Section 7, optional) scores
   against in-situ obs.
2. **`sftools/run_validation.py`** (automated, one cycle at a time — see
   below) — the exact same calls, headless, written to a JSON/text report
   plus a Taylor diagram PNG.
3. **`forecast/validate_all_cycles.sh`** (batch — see below) — calls
   `run_validation.py` for every not-yet-validated cycle.

Because all three go through the same two functions, they can't silently
disagree with each other. One correctness note worth knowing: CROCO's
`zeta` has no absolute geoid reference, so `godae_scorecard_croco_vs_glorys`
compares SSH **anomalies** (domain mean removed from both fields) by
default (`ssh_anomaly=True`) rather than raw levels — otherwise an
arbitrary offset between CROCO's and the reference's reference level would
show up as spurious "bias" that isn't a real skill difference.

### `02_validation.ipynb` — Section 6 (pass/fail) and Section 7 (in-situ)

Section 6's automated pass/fail summary reads directly from the Section 4
GODAE scorecard (`report`/`rows`) — not a separately-computed set of
statistics — so it can't drift out of sync with the Taylor diagram above
it, or with `run_validation.py`'s own report.

Section 7 is **optional and off by default** (`INSITU_FILES = None`): set
it to a glob pattern (e.g. CMEMS in-situ TAC files) to also score against
real observations, per GODAE depth layer. A cycle/region with no matching
in-situ profiles isn't a failure — the section just reports "nothing to
score" and moves on.

### `sftools/run_validation.py` (Step 4.1, one cycle)

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

### `forecast/validate_all_cycles.sh` (batch, every cycle)

Finds every cycle directory under `forecast/model-runs/<REGION>/` (or every
region if `--region` is omitted), skips any that already has a
`validation_report.json` (unless `--force`), and calls `run_validation.py`
on the rest. Appends one row per cycle to a running `validation_summary.csv`
per region — this is what `02_validation.ipynb` Section 8 loads to plot
criteria trends across cycles. Handles both existing cycle-directory naming
conventions in this repo (`run_forecast_cycle.sh`'s plain `YYYYMMDD`, and
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

### `forecast/install_validation_crontab.sh` (schedule the batch)

Installs (or updates) one cron entry that runs `validate_all_cycles.sh` on
a schedule, so new cycles get validated automatically without anyone
running the script by hand. Idempotent — re-running it replaces the
previous SEA-FORWARD-managed entry rather than adding a duplicate (a
marker comment tags the managed lines so any other cron jobs you have are
left untouched), and wraps the command in `flock` so a slow validation run
can never overlap with the next scheduled one.

```bash
cd forecast
./install_validation_crontab.sh                              # daily at 06:00 UTC
./install_validation_crontab.sh --schedule "0 */6 * * *"     # every 6 hours
./install_validation_crontab.sh --region Canary_12            # passed through to validate_all_cycles.sh
./install_validation_crontab.sh --remove                      # uninstall
crontab -l                                                     # verify
```

## Notebook-by-notebook notes

**`02_validation.ipynb`** — safe to run standalone. See "Validation: one
engine, three ways to run it" above for what's new; Section 8 is the
batch-history view (trigger `validate_all_cycles.sh` from the notebook,
or just load the CSV it produces).

**`03_exercises.ipynb`** — safe to run standalone, but references
`02_validation.ipynb`'s framing in its markdown. Each exercise's main code
cell is a fully worked reference implementation with `# TODO` comments
marking the physics/API lines to study; a short `assert`-based self-check
cell follows each one. This ships as the instructor/reference copy (it has
to execute cleanly end-to-end per the QA plan); to make a blanked
student handout, delete the marked answer lines yourself.

**`04_sensitivity.ipynb`** — Part A (perturb the wind forcing) and Part C
(compare the response) run for real in every mode. **Part B (the actual
CROCO re-run) is a genuine external step in real-data mode** — the
notebook cannot and does not fake it; it asserts clearly if the perturbed
run's output isn't found yet and tells you what to do. In demo mode, Part
B is skipped automatically and Part C compares against an auto-generated
synthetic "perturbed" run instead, so the notebook still executes
end-to-end.

**`05_animation.ipynb`** — safe to run standalone; needs **py-eddy-tracker**
(see "Before you start", above). Four animations built on `sftools.animate`:
SSH with detected eddies, current vectors, scalar fields (temperature/
salinity), and Lagrangian particle advection. Picks whichever matplotlib
animation writer is actually available (`ffmpeg` -> `.mp4`, else `pillow`
-> `.gif`) and displays the result inline; outputs land in
`notebooks/_animation_outputs/` (not committed — regenerate as needed).
Regridding the curvilinear CROCO grid every frame makes this noticeably
slower than the other notebooks on a full-size regional run.

## Language note (FR-09)

All markdown and docstrings in this folder are written in English.
French translation of the user-facing narrative text is coordinated
separately with the documentation team, so the English version here stays
the single source of truth for the code and doesn't drift out of sync
during translation.
