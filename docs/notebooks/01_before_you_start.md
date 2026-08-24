# Before You Start

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
