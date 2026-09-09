# Before You Start

1. **Activate the `seaforward` conda environment** and make sure `sftools` is
   installed editable from the repo root (`pip install --no-deps -e .` — see
   `sftools/README.md`). If `import sftools...` fails inside a notebook,
   this step was skipped.
2. **Launch Jupyter from the repository root**, not from inside `notebooks/`:
   ```bash
   cd seaforward        # repo root
   jupyter-lab
   ```
   Every notebook does `sys.path.insert(0, "..")` to resolve `import
   sftools`, which assumes the notebook's own working directory is
   `notebooks/` and the repo root is exactly one level up. Launching from
   inside `notebooks/` itself (`cd notebooks && jupyter-lab`) also works —
   what *doesn't* work is launching from anywhere else and browsing in, since
   Jupyter's working directory (not the file's location) is what `..`
   resolves against. 
3. Run notebooks **in numeric order** (02 before 03 before 04 before 05)
   the first time — later notebooks reuse conventions (the reference
   coastal point, the Bakun index) introduced earlier, and `05_sensitivity.ipynb`
   explicitly assumes you've run `04_exercises.ipynb`'s Exercise 1 first.
   `06_animation.ipynb` is independent of 03/04/05 and can be run any time
   after `02_validation.ipynb`; it only needs the same environment as every
   other notebook (`sftools.animation`).
4. Every notebook discovers its forecast cycle(s) itself via `_paths.py`
   (`SEAFORWARD_CONFIG`, `SEAFORWARD_MAIN_DIR`, `SEAFORWARD_CYCLE`
   environment variables, defaulting to region `Canary_12` and the most
   recent cycle found on disk) — there is no separate synthetic/demo-data
   fallback in the current notebooks. If no forecast cycles are found under
   `MAIN_DIR/CONFIG`, the notebook prints an empty cycle list and later
   cells will fail with a clear missing-file error; run a forecast (Phase 3)
   or point the environment variables at an existing `model-runs/` tree
   before continuing. 
