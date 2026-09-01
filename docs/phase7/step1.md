The child grid is built **exactly like the parent's** (Phase 2, Steps 1–2), just
with a smaller spacing and a slightly shrunk box so it sits inside the parent.

```bash
cd ${SEAFORWARD}/config
RES_25=$(echo "1/25" | bc -l)
python3 make_grid_config.py "Canary_25" -21.7 -15.8 14.3 23.7 ${RES_25} ${RES_25}
```

**What / Why:** the same generator as Phase 2 — `Canary_25` is even a built-in
example in `make_grid_config.py`. The box `-21.7 -15.8 14.3 23.7` is the parent's
(`-22 -15.5 14 24`) shrunk about 0.3° on each side, so the child sits comfortably
inside. `RES_25` is 1/25°, a little over twice the parent's 1/12° resolution.

Then build the grid, as in Phase 2 Step 2:

```bash
cd ${CROCO_PYTOOLS_DIR}/prepro
python3 make_grid.py ${CONFIG_DIR}/grid.ini 2>&1 | tail -5
ncdump -h ${CF}/croco_grd.nc | grep -E "xi_rho|eta_rho"
```

!!! check
    `xi_rho = 150`, `eta_rho = 238`. **Write these down** for `param.h`:

    - `LLm0 = xi_rho − 2 = 148`
    - `MMm0 = eta_rho − 2 = 236`

Now confirm the child really sits inside the parent — this is the one geometric
condition nesting depends on, and it is worth checking rather than assuming:

```bash
python3 -c "
import xarray as xr
c = xr.open_dataset('${CF}/croco_grd.nc')
p = xr.open_dataset('${CROCO_RUNS_ROOT}/Canary_12/CROCO_FILES/croco_grd.nc')
f = lambda d: (float(d.lon_rho.min()), float(d.lon_rho.max()),
               float(d.lat_rho.min()), float(d.lat_rho.max()))
print('CHILD  lon %.2f..%.2f  lat %.2f..%.2f' % f(c))
print('PARENT lon %.2f..%.2f  lat %.2f..%.2f' % f(p))
"
```

!!! check
    For Canary_25 against Canary_12:

```
    CHILD  lon -21.81..-15.69  lat 14.26..23.72
    PARENT lon -22.15..-15.35  lat 13.94..24.04
```

    The child is inside the parent on all four sides, with roughly 0.3° of margin. If any child edge falls outside, the boundary interpolation has no parent data to work from and the child will fail or produce nonsense at that edge.