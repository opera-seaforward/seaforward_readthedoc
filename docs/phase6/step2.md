Same file as Phase 2 Step 4, with two changes: **N=75** (was 50) and the NEST
prefixes. Create it in the child's `CROCO_FILES`:

```bash
nano ${CF}/crocotools_param.py
```

Type in:

```python
inputdata    = 'mercator'
Nzgoodmin    = 4
multi_files  = False
tracers      = ['temp', 'salt']
croco_grd    = 'croco_grd.nc'
sigma_params = dict(theta_s=7, theta_b=2, N=75, hc=200)
ini_prefix   = 'croco_ini_NEST'
bry_prefix   = 'croco_bry_NEST'
obc_dict     = dict(south=1, west=1, east=0, north=1)
cycle_bry    = 0
```

**Line by line — what changed from the parent:**

- `inputdata = 'mercator'` — **stays 'mercator'.** The parent's converted output
  *looks like* Mercator, so the same reader works. This is the trick that lets the
  whole Phase-2 chain treat your 1/12° run as if it were a global product.
- `sigma_params = dict(..., N=75, ...)` — **the vertical refinement.** The parent
  had `N=50`; the child has `N=75`. `theta_s/theta_b/hc` stay the same. **This one
  number is where the 50→75 refinement is defined** — `make_ini`/`make_bry` read it
  and interpolate the parent onto 75 child levels.
- `ini_prefix / bry_prefix = 'croco_ini_NEST' / 'croco_bry_NEST'` — names the child
  files distinctly from the parent's Mercator ones.
- `obc_dict` — **same boundaries as the parent** (E closed = African coast; S/W/N
  open). The child inherits the parent's open/closed pattern.

Keep a copy with the recipe:
```bash
cp ${CF}/crocotools_param.py ${CONFIG_DIR}/
```

!!! warning
    ⚠️ **WATCH — `N=75` must match everywhere.** As in Phase 2's consistency rules, the `N=75` here must equal the S-coord vertical count and the `N` in `param.h`. If they disagree, the model reads 75-level inputs into a differently-sized grid and crashes.