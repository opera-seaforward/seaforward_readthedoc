- **Multiple children.** AGRIF supports several per parent (somisana runs three); the
  `AGRIF_FixedGrids.in` format handles it directly. Untested here.
- **Nested levels.** `agrif_level = 2` for a child within a child.
- **Operational use.** Everything here is hand-assembled. Wiring AGRIF into a driver
  the way `run_forecast_igog.sh` does for the plain forecast is unbuilt.
- **Spun-up runs.** Every result above is one day from a Mercator cold start.