# Notebook-By-Notebook Notes

- **`01_seaforward_postprocess_plot.ipynb`** — safe to run standalone.
Static maps, sections, profiles, Hovmöller diagrams and time series built
on `sftools.postprocess` (`pp`) and `sftools.plotting` (`pl`); see Phase 5
for the full narrative walkthrough.

- **`02_validation.ipynb`** — safe to run standalone. See "Validation: one
engine, several ways to run it" for the section map.

- **`03_composite_validation.ipynb`** — merges **two or more** cycles
(`SEAFORWARD_CYCLES`, comma-separated, or every cycle found under
`MAIN_DIR/CONFIG` if left unset) into one lead-time-indexed composite. Safe
to run standalone after at least one forecast cycle exists; see "Composite
(multi-cycle) validation".

- **`04_exercises.ipynb`** — safe to run standalone, but references
`02_validation.ipynb`'s framing in its markdown. Each exercise's main code
cell is a fully worked reference implementation with `# TODO` comments
marking the physics/API lines to study; a short `assert`-based self-check
cell follows each one. This ships as the instructor/reference copy (it has
to execute cleanly end-to-end per the QA plan); to make a blanked
student handout, delete the marked answer lines yourself. Ends by pointing
you at `05_sensitivity.ipynb`.

- **`05_sensitivity.ipynb`** — Part A (perturb the wind forcing, ×1.5 per
Technical Specification Step 5.3) and Part C (compare the response) run
against whichever forecast cycle you point it at. **Part B (the actual
CROCO re-run) is a genuine external step** run outside the notebook, using
the same forecast orchestration script as Phase 3, pointed at the
perturbed forcing file Part A wrote — the notebook asserts clearly if
`fcst_wind1.5/CROCO_FILES/croco_his.nc` isn't found yet and tells you what
to do. Requires `04_exercises.ipynb` (at least Exercise 1) to have been run
first, since Part C reuses its Bakun-index calculation unchanged.

- **`06_animation.ipynb`** — safe to run standalone; no extra dependency
beyond the rest of the toolkit. Five animations built on the single
entry point `sftools.animation.animate()`: SST + wind stress, SSH +
currents, current speed + quivers, zonal current, meridional current. See
"Animation" for the section-by-section walkthrough and Phase 5's "Through
time" page for the full option reference.

