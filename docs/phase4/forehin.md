- **Same:** grid, mask, boundary decision, vertical coordinate, `param.h`,
  `jobcomp`, compiled binary mechanics, spin-up→run handoff, scratch/model-runs
  split.
- **Different:** ocean source (Mercator → **GLORYS**), atmosphere (GFS →
  **GFS**, `ERA_ECMWF`), `Yorig` (2000 → **1993**), data by **month** (not one
  anfc file), month-padding for GFS (`M01`), and the driver cycles a **past**
  window instead of running "today."
- **Kept separate on disk:** `forecast/` and `hindcast/` each have their own
  `configs/`, `scratch/`, `model-runs/`, and `track.sh`.