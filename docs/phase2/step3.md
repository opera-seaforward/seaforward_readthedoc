Each of your four boundaries is either **open** (water flows through — the model
reads ocean data there) or **closed** (a solid wall — because it's land). You
don't guess this; you read it from the mask.

Run this to *see* your boundaries as strips of ocean (`O`) and land (`.`):

```bash
python3 -c "
import xarray as xr
g=xr.open_dataset('${CF}/croco_grd.nc'); m=g.mask_rho.values
strip=lambda r: ''.join('O' if v==1 else '.' for v in r)
print('south:', int(m[0,:].sum()),'/',m.shape[1]); print('   W', strip(m[0,:]), 'E')
print('north:', int(m[-1,:].sum()),'/',m.shape[1]); print('   W', strip(m[-1,:]), 'E')
print('west :', int(m[:,0].sum()),'/',m.shape[0]);  print('   S', strip(m[:,0]), 'N')
print('east :', int(m[:,-1].sum()),'/',m.shape[0]); print('   S', strip(m[:,-1]), 'N')
"
```

**Mostly `O` → open (write `1`). Mostly `.` → closed (write `0`).**

!!! check
    **Canary_12 reads:**

    - west: 123/123 ocean → **open (1)**
    - east: ~1/123 ocean — it's the African coast → **closed (0)**
    - north: 77/81 ocean → **open (1)**
    - south: 67/81 ocean → **open (1)**

So your boundary setting is **south=1, west=1, east=0, north=1**. You will write it
twice — as `obc_dict` in `crocotools_param.py` (Step 4) and as the `OBC_*` switches
in `cppdefs.h` (Step 7) — and it also decides which boundaries `make_bry` builds
data for. All three must agree.

**Why it matters:** opening a boundary that's actually land is meaningless and
can make the model unstable. Closing a boundary that's really open starves the
model of inflow. The mask tells you the truth for *your* box.