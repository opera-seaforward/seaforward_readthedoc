The São Tomé child is the easy case: all four edges in deep open water. A coastal
child is harder and more typical.

**Box:** 6–10.5°E, 2°S–4.2°N — São Tomé, Príncipe, **Bioko**, and the Cameroon/Gabon
shelf. At 1/36° that's 167 × 260 × 50, about six times the São Tomé child.

The tool marched the north edge from the requested `jmax = 124` (4.21°N) to **133**
(4.94°N), onto the continent. The resulting grid:

```
S: 130/167  MIXED(37 land)   -> open
N:   0/167  ALL LAND         -> closed
W: 238/260  MIXED(22 land)   -> open
E:   0/260  ALL LAND         -> closed
```

Two open boundaries with land in them. Is that usable?

**Check the reference implementation.** somisana's `sa_eez_01` runs three AGRIF
children operationally along the South African coast. Their child grids are on disk,
so you can inspect them the same way:

```python
import xarray as xr, numpy as np
BASE = '~/SeaForward/code/somisana-croco/configs/sa_eez_01/croco_v2.0.1'
for n in [1, 2, 3]:
    f = '%s/GRID.%d/croco_grd.nc.%d' % (BASE, n, n)
    g = xr.open_dataset(f); m = g.mask_rho.values
    print('=== child %d:  %d x %d   ocean %.1f%%'
          % (n, m.shape[1], m.shape[0], float(m.mean()) * 100))
    for e, v in [('S', m[0, :]), ('N', m[-1, :]), ('W', m[:, 0]), ('E', m[:, -1])]:
        tag = ('all water' if v.all() else
               'ALL LAND'  if v.sum() == 0 else
               'MIXED(%d land)' % int((v == 0).sum()))
        print('    %s: %3d/%3d  %s' % (e, int(v.sum()), len(v), tag))
```
```
child 1:  S: 635/635 all water   N: 0/635 ALL LAND   W: MIXED(25)  E: MIXED(25)
child 2:  S: 332/332 all water   N: 0/332 ALL LAND   W: MIXED(40)  E: MIXED(22)
child 3:  S: 362/362 all water   N: 0/362 ALL LAND   W: MIXED(25)  E: MIXED(49)
```

Every one has mixed edges. Child 3's east edge is **half land**. These are
coast-parallel strips: offshore edge open, landward edge closed on genuine coast, and
the two cross-shore edges necessarily mixed — because they run from deep water up
onto the beach. There is no other way to build a coastal nest.

So mixed open boundaries are fine, and `easygrid.py`'s march is over-conservative
relative to what CROCO actually accepts. The coastal child ran:

```
0  9688.00000 2.466581524E-03  2.1948393E+15  0    <- parent
0  9688.00000 2.655962656E-03  5.0222441E+14  0    <- child, same clock, sane KE
```

with clocks locked 3:1 and both grids stable.

**The lesson:** when a tool refuses to build something, check whether a working
system does it anyway before redesigning around the refusal.