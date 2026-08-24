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
