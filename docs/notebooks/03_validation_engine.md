# Validation: One Engine, Three Ways To Run It

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

## 02_validation.ipynb — Section 6 (pass/fail) and Section 7 (in-situ)

Section 6's automated pass/fail summary reads directly from the Section 4
GODAE scorecard (`report`/`rows`) — not a separately-computed set of
statistics — so it can't drift out of sync with the Taylor diagram above
it, or with `run_validation.py`'s own report.

Section 7 is **optional and off by default** (`INSITU_FILES = None`): set
it to a glob pattern (e.g. CMEMS in-situ TAC files) to also score against
real observations, per GODAE depth layer. A cycle/region with no matching
in-situ profiles isn't a failure — the section just reports "nothing to
score" and moves on.
