# Demo Data

Read this if a notebook complains about missing files.

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
