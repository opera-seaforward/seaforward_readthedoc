# notebooks/ — SEA-FORWARD Jupyter Notebook Toolkit

Guided, interactive counterparts to the automated pipeline (Steps 1-5 of the
operational workflow, `sftools.cli` / `sftools/run_validation.py`). Owned by
Python Dev 1/2, DCC processes **V1** (validation) and **D1** (downstream
post-processing, exercises, sensitivity analysis, animation).

``` { .text .no-copy }
notebooks/
├── 01_seaforward_postprocess_plot.ipynb  ← maps, sections, profiles, Hovmöller,
│                                            time series (D1)
├── 02_validation.ipynb                   ← single-cycle validation: bias maps,
│                                            scatter plots, Taylor diagrams, time
│                                            series, pass/fail summary, optional
│                                            in-situ scoring, HTML report, batch
│                                            history across cycles (V1)
├── 03_composite_validation.ipynb         ← multi-cycle validation, merged and
│                                            indexed by forecast LEAD TIME rather
│                                            than calendar date (V1)
├── 04_exercises.ipynb                    ← guided exercises: upwelling index,
│                                            MLD, coastal jet, eddy detection (D1)
├── 05_sensitivity.ipynb                  ← wind-forcing sensitivity study,
│                                            Step 5.3 (U3 -> C1 -> D1)
├── 06_animation.ipynb                    ← 5 animations built on a single entry
│                                            point, sftools.animation.animate()
│                                            (D1)
├── _paths.py                             ← shared helper, NOT a notebook — cycle
│                                            discovery + path resolution, see below
└── region_cells.py                       ← region-picker helper cells

sftools/
├── validation.py                 ← single module for every single-cycle validation
│                                    building block: bias maps, profiles, scatter,
│                                    GODAE scorecard/Taylor diagram, satellite
│                                    SST/SSS, optional in-situ, HTML summary
│                                    (imported as `val` in 02_validation.ipynb and
│                                    03_composite_validation.ipynb — some of that
│                                    module's docstrings/prose refer to logical
│                                    sub-areas as "validation_godae"/
│                                    "validation_satellite"; there is no separate
│                                    top-level module by either of those names)
├── validation_composite.py       ← lead-time compositing across cycles (imported
│                                    as `vc` in 03_composite_validation.ipynb only)
├── download/cmems.py             ← Copernicus Marine availability checks + downloads
│                                    (`from sftools.download import cmems`)
├── animation.py                  ← sftools.animation.animate() — the single entry
│                                    point behind every animation in 06_animation.ipynb
└── run_validation.py             ← validates ONE cycle (Step 4.1) -- see below

forecast/
├── validate_all_cycles.sh           ← validates EVERY not-yet-validated cycle
└── install_validation_crontab.sh    ← schedules validate_all_cycles.sh via cron

validation/
└── test_sftools_animate_validation.py   ← pytest suite for validation_godae.py / animation.py
```

!!! warning
    **Module name: `sftools.animation`, not `sftools.animate`.** `06_animation.ipynb`
    imports `sftools.animation` — if your checkout only has an older
    `sftools/animate.py`, update to the revision that ships `sftools/animation.py`,
    or adjust the notebook's import. Older material (including some pages in this
    Toolkit section) may still say `animate.py`; treat `sftools.animation` as
    current.

**A note on `validation/`:** `validation_godae.py` and (the historical)
`animate.py` used to also have stale duplicate copies under `validation/`
(left over from early development, before they were finalised) — those have
been removed. `sftools/` is the single source of truth for every importable
module; `validation/` holds only the test suite.

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
3. Run notebooks **in numeric order** (02 before 03 before 04 before 05)
   the first time — later notebooks reuse conventions (the reference
   coastal point, the Bakun index) introduced earlier, and `05_sensitivity.ipynb`
   explicitly assumes you've run `04_exercises.ipynb`'s Exercise 1 first.
   `06_animation.ipynb` is independent of 03/04/05 and can be run any time
   after `02_validation.ipynb`; it only needs the same environment as every
   other notebook (`sftools.animation`) — no extra package like
   py-eddy-tracker is required.
4. Every notebook discovers its forecast cycle(s) itself via `_paths.py`
   (`SEAFORWARD_CONFIG`, `SEAFORWARD_MAIN_DIR`, `SEAFORWARD_CYCLE`
   environment variables, defaulting to region `Canary_12` and the most
   recent cycle found on disk) — there is no separate synthetic/demo-data
   fallback in the current notebooks. If no forecast cycles are found under
   `MAIN_DIR/CONFIG`, the notebook prints an empty cycle list and later
   cells will fail with a clear missing-file error; run a forecast (Phase 3)
   or point the environment variables at an existing `model-runs/` tree
   before continuing. See "Demo Data" for how to override the defaults.

## Demo data / paths — read this if a notebook complains about missing files

Read this if a notebook complains about a missing file or an empty cycle list.

!!! warning "This page used to describe `_demo_data.py` / synthetic demo data"
    Earlier revisions of this Toolkit generated a small synthetic stand-in
    (fake CROCO history, fake GLORYS reference, fake wind field) whenever
    real data wasn't found, and printed a `!! DEMO DATA !!` banner. **The
    current notebooks (`02_validation.ipynb` through `06_animation.ipynb`)
    no longer do this** — there is no `_demo_data.py` and no synthetic
    fallback. If your checkout still has `notebooks/_demo_data.py` and
    notebooks that import it, you're looking at an older revision of the
    toolkit; the rest of this page describes the current behaviour.

Every current notebook imports the shared helper `_paths.py` (not a
notebook itself) instead. Each notebook's setup cell reads three
environment variables, all optional:

| Variable | Default | Meaning |
| --- | --- | --- |
| `SEAFORWARD_CONFIG` | `Canary_12` | region/configuration name |
| `SEAFORWARD_MAIN_DIR` | `~/seaforward/forecast/model-runs` (`~/seaforward/hindcast/model-runs` for hindcast-mode notebooks) | root of the `model-runs/<CONFIG>/<CYCLE>/...` tree |
| `SEAFORWARD_CYCLE` | the most recent cycle `_paths.list_cycles()` finds under `MAIN_DIR/CONFIG` | which `YYYYMMDD` cycle directory to open |

`_paths.list_cycles(main_dir, config)` scans `MAIN_DIR/CONFIG` for
subdirectories named `YYYYMMDD` and returns the ones that actually contain
a `CROCO_FILES/croco_his.nc` — this is what every notebook prints near the
top ("forecast cycles found under ..."). `_paths.get_paths(cycle=, config=,
main_dir=)` resolves the exact `CROCO_HIS` / `REFERENCE` file paths for one
cycle.

**If the printed cycle list is empty**, there is no synthetic fallback any
more — later cells will fail with a plain missing-file error (or, in
`02_validation.ipynb`/`03_composite_validation.ipynb`, the availability
guard will simply skip every reference-product comparison). Either:

- run a forecast first (Phase 3) so a real cycle exists under the default
  path, or
- point the environment variables at an existing `model-runs/` tree before
  launching Jupyter:

```bash
export SEAFORWARD_CONFIG=Canary_12
export SEAFORWARD_MAIN_DIR=~/seaforward/forecast/model-runs
export SEAFORWARD_CYCLE=20260711
jupyter lab
```

`06_animation.ipynb` uses the same `_paths.py` pattern but additionally
sets `SEAFORWARD_RUN_TYPE` (`fcst` or `hcast`, default `fcst`) to pick
between the forecast and hindcast trees, since its example historically
pointed at a hindcast run.

## Validation: one engine, several ways to run it

`sftools.validation_godae` -- the GODAE OceanView scorecard (bias, RMSD,
unbiased RMSD, correlation, two scatter-index variants, std-ratio) plus
optional class-4 in-situ scoring per depth layer -- is now the **single
statistics engine** behind every validation surface in this repo:

``` { .text .no-copy }
sftools.validation_godae.godae_scorecard_croco_vs_glorys()   <- grid vs reference, one variable
sftools.validation_godae.validate_against_insitu()           <- grid vs CMEMS in-situ TAC, per depth layer
```

...used identically by:

1. **`02_validation.ipynb`** (interactive, single cycle, Sections 2-4) —
   builds the same scorecard, draws the Taylor diagram, and (Section 8,
   optional) scores against in-situ obs.
2. **`03_composite_validation.ipynb`** (interactive, multi-cycle) — the
   same single-cycle building blocks from `sftools.validation`, called
   through `sftools.validation_composite` (module `vc`) to merge several
   cycles by **forecast lead time** rather than calendar date — see
   "Composite (multi-cycle) validation".
3. **`sftools/run_validation.py`** (automated, one cycle at a time — see
   below) — the exact same calls, headless, written to a JSON/text report
   plus a Taylor diagram PNG.
4. **`forecast/validate_all_cycles.sh`** (batch — see below) — calls
   `run_validation.py` for every not-yet-validated cycle.

Because all four go through the same statistics engine, they can't silently
disagree with each other. One correctness note worth knowing: CROCO's
`zeta` has no absolute geoid reference, so the SSH comparison is done on
**anomalies** (domain mean removed from both fields) rather than raw
levels — otherwise an arbitrary offset between CROCO's and the reference's
reference level would show up as spurious "bias" that isn't a real skill
difference.

## 02_validation.ipynb — section map

The notebook's actual section numbering (current revision):

| Section | What it does |
| --- | --- |
| 1 | Load model output, grid/time sanity check, numerical-stability check |
| 1b | Reference-product availability (Copernicus Marine: forecast parent, OSTIA, ODYSSEA, SMOS) — a metadata-only check, nothing is skipped here yet |
| 1c | Downloads the reference products for this cycle into `downloaded_data/` |
| 2 | Bias maps — CROCO vs Copernicus Marine Forecast parent (SST, SSH, currents, SSS) |
| 2b / 2b-bis | Vertical profile & error-vs-depth, point and full-domain |
| 2c | Depth-resolved comparison at 4 levels (surface, 120 m, 300 m, 1000 m) |
| 3 | Scatter plots, pointwise CROCO vs parent |
| 4 | GODAE scorecard + Taylor diagram |
| **5** | **Automated pass/fail summary (V1)** — reads directly from the Section 4 scorecard, so it can't drift out of sync with the Taylor diagram or with `run_validation.py`'s own report |
| 6 / 6b / 6c | Time series and domain-wide bias boxplots, vs parent and vs satellite |
| 7 / 7b | Satellite SST (OSTIA, ODYSSEA) and SSS (SMOS) validation |
| **8** | **In-situ validation (optional)** — off by default; a cycle/region with no matching in-situ profiles isn't a failure, the section just reports "nothing to score" and moves on |
| 9 | Self-contained HTML summary report (`index.html`) |
| 10 | Batch validation across every forecast cycle, via `forecast/validate_all_cycles.sh` |

Every reference-product comparison in Sections 2 onward is
**availability-guarded**: if `AVAIL['mercator_forecast']` (or the relevant
satellite flag) is `False`, that section is skipped and says why, rather
than raising an error — a temporary CMEMS outage or missing credentials is
not a V1 validation failure.

<div style="display:flex; justify-content:center; margin:10px 0 14px 0;">
   <a href="https://raw.githubusercontent.com/opera-seaforward/seaforward_readthedoc/main/docs/notebooks/02_validation.ipynb" data-download-url="https://raw.githubusercontent.com/opera-seaforward/seaforward_readthedoc/main/docs/notebooks/02_validation.ipynb" data-download-filename="02_validation.ipynb" onmouseover="this.style.transform='scale(1.08)'; this.style.boxShadow='0 10px 24px rgba(0,0,0,0.18)';" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none';" style="display:inline-flex; align-items:center; justify-content:center; gap:16px; min-width: 80px; padding:20px 20px; border-radius:10px; background:linear-gradient(to bottom, #ffffcc 0%, #f4f797de 100%); color:#000000; text-decoration:none; font-size:1.2rem; line-height:1.1; text-align:center; transition:transform 0.18s ease, box-shadow 0.18s ease; transform-origin:center;">
      <img src="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/download.svg" alt="" aria-hidden="true" style="width:25px; height:25px; color:#000000; font-weight:bold filter:invert(1);" />
      <span>Download notebook 02_validation.ipynb</span>
   </a>
</div>

## Notebook-by-notebook notes

!!! warning "Superseded claims removed from this page"
    Earlier revisions of this page described a synthetic "demo mode"
    (`_demo_data.py`), a py-eddy-tracker-based animation notebook with
    eddy detection and particle advection, and notebooks numbered
    `03_exercises.ipynb` / `04_sensitivity.ipynb` / `05_animation.ipynb`.
    None of that matches the current notebook set — see below.

**`01_seaforward_postprocess_plot.ipynb`** — safe to run standalone.
Static maps, sections, profiles, Hovmöller diagrams and time series built
on `sftools.postprocess` (`pp`) and `sftools.plotting` (`pl`); see Phase 5
for the full narrative walkthrough.

**`02_validation.ipynb`** — safe to run standalone. See "Validation: one
engine, several ways to run it" for the section map; Section 10 is the
batch view across every forecast cycle (`forecast/validate_all_cycles.sh`).

**`03_composite_validation.ipynb`** — merges **two or more** cycles
(`SEAFORWARD_CYCLES`, comma-separated, or every cycle found under
`MAIN_DIR/CONFIG` if left unset) into one lead-time-indexed composite. Safe
to run standalone after at least one forecast cycle exists; see "Composite
(multi-cycle) validation".

**`04_exercises.ipynb`** — safe to run standalone, but references
`02_validation.ipynb`'s framing in its markdown. Each exercise's main code
cell is a fully worked reference implementation with `# TODO` comments
marking the physics/API lines to study; a short `assert`-based self-check
cell follows each one. This ships as the instructor/reference copy (it has
to execute cleanly end-to-end per the QA plan); to make a blanked
student handout, delete the marked answer lines yourself. Ends by pointing
you at `05_sensitivity.ipynb`.

**`05_sensitivity.ipynb`** — Part A (perturb the wind forcing, ×1.5 per
Technical Specification Step 5.3) and Part C (compare the response) run
against whichever forecast cycle you point it at. **Part B (the actual
CROCO re-run) is a genuine external step** run outside the notebook, using
the same forecast orchestration script as Phase 3, pointed at the
perturbed forcing file Part A wrote — the notebook asserts clearly if
`fcst_wind1.5/CROCO_FILES/croco_his.nc` isn't found yet and tells you what
to do. Requires `04_exercises.ipynb` (at least Exercise 1) to have been run
first, since Part C reuses its Bakun-index calculation unchanged.

**`06_animation.ipynb`** — safe to run standalone; no extra dependency
beyond the rest of the toolkit (in particular, **no py-eddy-tracker** — an
earlier revision's animation notebook did eddy detection and particle
advection, the current one doesn't). Five animations built on the single
entry point `sftools.animation.animate()`: SST + wind stress, SSH +
currents, current speed + quivers, zonal current, meridional current. See
"Animation" for the section-by-section walkthrough and Phase 5's "Through
time" page for the full option reference.

## Language Note (FR-09)

All markdown and docstrings in this folder are written in English.
French translation of the user-facing narrative text is coordinated
separately with the documentation team, so the English version here stays
the single source of truth for the code and doesn't drift out of sync
during translation.
