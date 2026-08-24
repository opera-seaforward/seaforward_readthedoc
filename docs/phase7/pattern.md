Building any region is the same recipe with a few swapped values:

| Always changes per region | Always the same |
|---|---|
| Box (lon/lat extent) | Vertical grid structure (θ_s=7, θ_b=2, hc=200) |
| Grid size (LLm0, MMm0) | The four config files' structure |
| Open/closed boundaries (from the mask) | The compile (jobcomp, opt_seq NetCDF) |
| `FIX_GFS_LON` (hemisphere) | The forecast driver machinery |
| Physical regime (upwelling, equatorial, WBC…) | make_ini / make_bry / patch_croco_in |

So a new region is: pick the box → build the grid → read the boundaries → set
`FIX_GFS_LON` → copy + edit the four config files → compile → run. Each card above is
that process, frozen at the "here's the result" stage.