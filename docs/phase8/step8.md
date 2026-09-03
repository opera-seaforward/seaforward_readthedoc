Second milestone. Attempt this only once Step 7 gives you two clean `MAIN: DONE` —
otherwise you are debugging the nest and the feedback at once.

### 8a — Save the baseline first

The two-way run overwrites `CROCO_FILES/croco_his.nc`. Without a copy of the one-way
result you have nothing to compare against, and the exercise has no point.

```bash
cd ~/seaforward/forecast/scratch/Canary_AGRIF
mkdir -p oneway
cp CROCO_FILES/croco_his.nc   oneway/
cp CROCO_FILES/croco_his.nc.1 oneway/
ls -lh oneway/
```

### 8b — Flip the flag

```bash
nano cppdefs.h
```

`Ctrl+W` `AGRIF_2WAY` `Enter` — again the **first** match, near line 81:

```text
# define AGRIF
# undef  AGRIF_2WAY        <- change to "# define AGRIF_2WAY"
```

becomes

```text
# define AGRIF
# define AGRIF_2WAY
```

`Ctrl+O` `Enter`, `Ctrl+X`. Verify:

```bash
grep -n "AGRIF" cppdefs.h | head -2
```

```text
80:# define AGRIF
81:# define AGRIF_2WAY      <- feedback on
```

That one word is the entire difference between one-way and two-way.

### 8c — Recompile and rerun

A `cppdefs.h` change means a **full rebuild** — the flag changes which code is
compiled, not a runtime setting.

```bash
conda deactivate
source ~/seaforward/env.sh
./jobcomp 2>&1 | tail -3
# ... CROCO is OK
cp croco croco_2way

nohup ./croco croco.in > run_agrif_2way.log 2>&1 &
```

Keep the binary under its own name. You now have `croco_1way` and `croco_2way`, which
is what the operational driver expects — it selects between them by name, so both
modes stay available without recompiling.

Nothing else changes: same grids, same ICs, same `croco.in` and `croco.in.1`. That is
what makes it a clean experiment — one variable.

### 8d — Check the feedback is engaging

```bash
sleep 60
tail run_agrif_2way.log
```

Compare the parent's kinetic energy against the one-way run at the same step. **If
two-way gives a bit-identical number the feedback is not doing anything**, and
something is wrong — the parent should begin diverging within a few steps of receiving
the child's solution.

For this run, at parent step 196:

```text
one-way   KE 1.530e-03    NET_VOLUME 1.83197e+15
two-way   KE 1.625e-03    NET_VOLUME 1.83591e+15
```

The parent's kinetic energy is about 6% higher with feedback on, and its volume has
shifted in the fifth significant figure. The child is changing the parent's solution,
which is the whole point.

Watch for instability too. Two-way injects fine-grid values into a coarse grid every
step; if the grids disagree at the interface it can ring. The blowup counter and the
kinetic energy are the early warning — here `trd` stays 0 throughout and the energy
climbs smoothly rather than jumping.

Success is again **two** `MAIN: DONE`:

```bash
grep -c "MAIN: DONE" run_agrif_2way.log
```

### 8e — The difference plot

This is the point of running both: the parent's solution with and without the child
feeding back.

Check first that the two runs cover the same window, or the last record of each is a
different instant:

```bash
cd ~/seaforward
python3 << 'PYEOF'
import xarray as xr
B = 'forecast/scratch/Canary_AGRIF/'
for f, l in [('oneway/croco_his.nc', 'one-way parent'),
             ('CROCO_FILES/croco_his.nc', 'two-way parent')]:
    d = xr.open_dataset(B + f, decode_times=False)
    t = d.scrum_time.values / 86400
    print('%-16s %2d records  %.4f .. %.4f' % (l, len(t), t[0], t[-1]))
PYEOF
```

```text
one-way parent    5 records  9686.0000 .. 9687.0000
two-way parent    5 records  9686.0000 .. 9687.0000
```

Then plot:

```bash
cd ~/seaforward
python3 << 'PYEOF'
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, xarray as xr, numpy as np

B  = 'forecast/scratch/Canary_AGRIF/'
p1 = xr.open_dataset(B + 'oneway/croco_his.nc',        decode_times=False)
p2 = xr.open_dataset(B + 'CROCO_FILES/croco_his.nc',   decode_times=False)
c  = xr.open_dataset(B + 'CROCO_FILES/croco_his.nc.1', decode_times=False)

s1 = p1.temp.isel(time=-1, s_rho=-1).where(p1.mask_rho == 1)
s2 = p2.temp.isel(time=-1, s_rho=-1).where(p2.mask_rho == 1)
d  = s2 - s1
print('max |two-way - one-way| SST = %.4f C' % float(np.nanmax(np.abs(d))))

x0, x1 = float(c.lon_rho.min()), float(c.lon_rho.max())
y0, y1 = float(c.lat_rho.min()), float(c.lat_rho.max())

fig, ax = plt.subplots(1, 3, figsize=(17, 6), constrained_layout=True)

ax[0].pcolormesh(p1.lon_rho, p1.lat_rho, s1, cmap='RdYlBu_r', vmin=18, vmax=28)
ax[0].set_title('parent, one-way')
a1 = ax[1].pcolormesh(p2.lon_rho, p2.lat_rho, s2, cmap='RdYlBu_r', vmin=18, vmax=28)
ax[1].set_title('parent, two-way')
fig.colorbar(a1, ax=ax[:2], label='SST (C)', shrink=0.8, pad=0.02)

a2 = ax[2].pcolormesh(p1.lon_rho, p1.lat_rho, d, cmap='RdBu_r', vmin=-0.4, vmax=0.4)
ax[2].set_title('two-way minus one-way')
fig.colorbar(a2, ax=ax[2], label='dSST (C)', shrink=0.8, pad=0.02, extend='both')

for a in ax:
    a.plot([x0,x1,x1,x0,x0], [y0,y0,y1,y1,y0], 'k-', lw=1.5)
    a.set_aspect('equal'); a.set_xlabel('longitude')
ax[0].set_ylabel('latitude')
fig.savefig('docs/img/agrif_2way_diff.png', dpi=110)
PYEOF
```

![The parent with and without feedback](../img/agrif_2way_diff.png)

*The parent's surface temperature after one day, one-way and two-way, and the
difference. The child's footprint is outlined on all three.*

The two SST panels look nearly identical, which is the honest result at one day. The
difference panel is where the feedback shows.

**The correction sits inside the box**, and within it concentrates along the coastal
upwelling strip near 17°W between 19 and 22°N — the sharp temperature gradients the
child resolves and the parent smooths. Faint traces spread west and south-west;
outside the box the field is nearly white.

Direct correction where the grids overlap, then propagation outward as the parent's
own advection carries the corrected water away. That second part is what offline
nesting structurally cannot do.