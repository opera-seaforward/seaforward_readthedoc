The child grid is built **exactly like the parent's** (Phase 2, Steps 1–2), just
with a smaller spacing and a slightly shrunk box so it sits inside the parent.

```bash
cd ${SEAFORWARD}/config
RES_25=$(echo "1/25" | bc -l)
python3 make_grid_config.py "Canary_25" -21.7 -15.8 14.3 23.7 ${RES_25} ${RES_25}
```

**What / Why:** same generator as Phase 2 — `Canary_25` is even a built-in example
in `make_grid_config.py`. The box `-21.7 -15.8 14.3 23.7` is the parent's box
(`-22 -15.5 14 24`) shrunk ~0.3° on each side, so the child sits comfortably
inside. `RES_25` is 1/25° (~half the parent's 1/12°).

Then build the grid (Phase 2, Step 2):

```bash
cd ${CROCO_PYTOOLS_DIR}/prepro
python3 make_grid.py ${CONFIG_DIR}/grid.ini 2>&1 | tail -5
ncdump -h ${CF}/croco_grd.nc | grep -E "xi_rho|eta_rho"
```

!!! check
    ✅ **CHECK** — `xi_rho = 150`, `eta_rho = 238`. **Write these down** for `param.h`:
     - `LLm0 = xi_rho − 2 = 148`
     - `MMm0 = eta_rho − 2 = 236`

Confirm the child really sits inside the parent:

```bash
python3 -c "
import xarray as xr
c = xr.open_dataset('${CF}/croco_grd.nc')
print('CHILD  lon %.2f..%.2f  lat %.2f..%.2f' % (
    float(c.lon_rho.min()), float(c.lon_rho.max()),
    float(c.lat_rho.min()), float(c.lat_rho.max())))
print('PARENT lon -22.15..-15.35  lat 13.94..24.04  (child must be inside)')
"
```

!!! check
    ✅ The child range (~−22.1..−15.4, ~13.96..24.0) is inside the parent's.