Second milestone. Only attempt this once Step 7 gives you two clean `MAIN: DONE` —
otherwise you're debugging the nest and the feedback at once.

### 8a — save the baseline first

The two-way run will overwrite `CROCO_FILES/croco_his.nc`. Without a copy of the
one-way result you have nothing to compare against, and the whole exercise is
pointless.

```bash
cd ~/seaforward/forecast/scratch/IGOG_AGRIF
mkdir -p oneway
cp CROCO_FILES/croco_his.nc   oneway/
cp CROCO_FILES/croco_his.nc.1 oneway/
ls -lh oneway/
```

### 8b — flip the flag

```bash
nano cppdefs.h
```

`Ctrl+W` `AGRIF_2WAY` `Enter` — again, the **first** match, near line 81:

```
# define AGRIF
# undef  AGRIF_2WAY        <- change to "# define AGRIF_2WAY"
```
→
```
# define AGRIF
# define AGRIF_2WAY
```

`Ctrl+O` `Enter`, `Ctrl+X`.

```bash
grep -n "AGRIF" cppdefs.h | head -2
```
```
80:# define AGRIF
81:# define AGRIF_2WAY      <- feedback on
```

That one word is the entire difference between one-way and two-way.

### 8c — recompile and rerun

A cppdefs change means a **full rebuild** — the flag changes which code gets
compiled, not a runtime setting.

```bash
conda deactivate
source ./config.sh
./jobcomp 2>&1 | tail -3
# ... CROCO is OK

nohup ./croco croco.in > run_2way.log 2>&1 &
```

Nothing else changes — same grids, same ICs, same `croco.in` and `croco.in.1`. That's what makes it a clean experiment: one variable.

### 8d — check the feedback is actually engaging

```bash
sleep 60
grep -E "^ +25 +9688\." run_2way.log
```

Compare the parent's KE against the one-way run at the same step. In the São Tomé
example, one-way step 25 was `2.469078679E-03`. **If two-way gives a bit-identical
number, the feedback isn't doing anything** and something is wrong — the parent
should start diverging within a few steps of receiving the child's solution.

Also watch for instability. Two-way injects fine-grid values into a coarse grid every
step; if the grids disagree at the interface it can ring. The blowup counter and KE
are the early warning.

### The difference plot — the whole point

```python
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, xarray as xr, numpy as np

B  = 'forecast/scratch/IGOG_AGRIF/'
p1 = xr.open_dataset(B + 'oneway/croco_his.nc',      decode_times=False)
p2 = xr.open_dataset(B + 'CROCO_FILES/croco_his.nc', decode_times=False)
c  = xr.open_dataset(B + 'CROCO_FILES/croco_his.nc.1', decode_times=False)

s1 = p1.temp.isel(time=-1, s_rho=-1).where(p1.mask_rho == 1)
s2 = p2.temp.isel(time=-1, s_rho=-1).where(p2.mask_rho == 1)
d  = s2 - s1
lim = float(np.nanmax(np.abs(d)))
print('max |parent_2way - parent_1way| SST = %.4f C' % lim)

fig, ax = plt.subplots(figsize=(7, 6), constrained_layout=True)
m = ax.pcolormesh(p1.lon_rho, p1.lat_rho, d, cmap='RdBu_r', vmin=-lim, vmax=lim)
ax.plot([float(c.lon_rho.min()), float(c.lon_rho.max()), float(c.lon_rho.max()),
         float(c.lon_rho.min()), float(c.lon_rho.min())],
        [float(c.lat_rho.min()), float(c.lat_rho.min()), float(c.lat_rho.max()),
         float(c.lat_rho.max()), float(c.lat_rho.min())], 'k-', lw=1.5)
ax.set_title('parent SST: two-way minus one-way (1 day)')
fig.colorbar(m, ax=ax, label='dSST (C)')
fig.savefig('docs/img/agrif_2way_diff.png', dpi=110)
```

![two-way minus one-way](img/agrif_2way_diff.png)

*The parent's SST, two-way minus one-way, after one day. Strongest signal (±0.5 °C) inside the child box, concentrated around São Tomé — the child telling the parent about a wake it never computed. Outside the box, a scatter of smaller differences trails south and west: water the child never touched, carried there by the parent's own advection. Direct correction in the box; indirect propagation beyond it.*

Read it honestly: 0.5 °C after one day from a cold start is modest, and the speckled texture suggests some of it is grid-scale noise from the feedback rather than clean physics. A longer, spun-up run would separate signal from adjustment. But the core result stands — **the parent's solution changed, most where the child is, and it spread**. That is what offline nesting structurally cannot do.
