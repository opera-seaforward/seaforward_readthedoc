- **Same:** grid, mask, boundary decision, vertical coordinate, `param.h`,
  `jobcomp`, compiled binary mechanics, spin-up→run handoff, scratch/model-runs
  split.
- **Different:** ocean source (Mercator → **GLORYS**), atmosphere (GFS →
  **ERA5**, which needs `ERA_ECMWF` defined in `cppdefs.h`), `Yorig`
  (2000 → **1993**), data arriving by **month** rather than as one merged file,
  month-padding in the ERA5 filenames (`M01`), and a driver that cycles a **past**
  window instead of running "today".
- **Kept separate on disk:** `forecast/` and `hindcast/` each have their own
  `configs/`, `scratch/`, `model-runs/` and `track.sh`.