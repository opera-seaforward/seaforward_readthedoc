# Notebook-By-Notebook Notes

**`02_validation.ipynb`** — safe to run standalone. See "Validation: one
engine, three ways to run it" for what's new; Section 8 is the
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

**`05_animation.ipynb`** — safe to run standalone; needs
**py-eddy-tracker** (see "Before you start"). Four animations built on
`sftools.animate`: SSH with detected eddies, current vectors, scalar
fields (temperature/salinity), and Lagrangian particle advection. Picks
whichever matplotlib animation writer is actually available (`ffmpeg` ->
`.mp4`, else `pillow` -> `.gif`) and displays the result inline; outputs
land in `notebooks/_animation_outputs/` (not committed — regenerate as
needed). Regridding the curvilinear CROCO grid every frame makes this
noticeably slower than the other notebooks on a full-size regional run.

## Language Note (FR-09)

All markdown and docstrings in this folder are written in English.
French translation of the user-facing narrative text is coordinated
separately with the documentation team, so the English version here stays
the single source of truth for the code and doesn't drift out of sync
during translation.
