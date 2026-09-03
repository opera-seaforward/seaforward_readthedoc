This step is entirely diagnostic — you write no config here. You interrogate the
parent's mask until you know where the child can go.

!!! important
    **Read the mask, not a plot.** A saturated colour map will make dry land look like ocean. A box chosen from an SST figure can land hundreds of kilometres inland. The mask is the only authority.

Run these from `~/seaforward`.

### 1a — The parent's dimensions

Every index below is relative to this grid, so start by reading it:

```bash
python3 << 'PYEOF'
import xarray as xr, numpy as np
g   = xr.open_dataset('forecast/scratch/Canary_12/CROCO_FILES/croco_grd.nc')
lon = g.lon_rho.values
lat = g.lat_rho.values
print('Canary_12: xi=%d eta=%d, lon %.2f-%.2fE, lat %.2f-%.2fN'
      % (lon.shape[1], lon.shape[0], lon.min(), lon.max(), lat.min(), lat.max()))
PYEOF
```

```text
Canary_12: xi=81 eta=123, lon -21.95--15.55E, lat 13.94-24.00N
```

### 1b — Test a candidate box

This converts a lon/lat box to parent indices and reports what you need to judge it:
the child size, the margin to the parent's edges, the ocean fraction, the depth range,
and the land/water pattern along each of the four edges.

```bash
python3 << 'PYEOF'
import xarray as xr, numpy as np
g   = xr.open_dataset('forecast/scratch/Canary_12/CROCO_FILES/croco_grd.nc')
lon = g.lon_rho.values[0, :]     # 1-D along xi
lat = g.lat_rho.values[:, 0]     # 1-D along eta
m   = g.mask_rho.values          # 1 = ocean, 0 = land
h   = g.h.values

def check(name, lo0, lo1, la0, la1, coef=3):
    imin = int(np.argmin(abs(lon - lo0))); imax = int(np.argmin(abs(lon - lo1)))
    jmin = int(np.argmin(abs(lat - la0))); jmax = int(np.argmin(abs(lat - la1)))
    sm = m[jmin:jmax+1, imin:imax+1]
    sh = h[jmin:jmax+1, imin:imax+1]

    print(name)
    print('  lon %.1f-%.1fE lat %.1f-%.1fN' % (lo0, lo1, la0, la1))
    print('  -> imin=%d imax=%d jmin=%d jmax=%d' % (imin, imax, jmin, jmax))
    print('  parent cells: %d x %d   child at %dx: %d x %d'
          % (imax-imin+1, jmax-jmin+1, coef,
             (imax-imin)*coef+1, (jmax-jmin)*coef+1))
    print('  margin to parent edge: W=%d E=%d S=%d N=%d cells'
          % (imin, m.shape[1]-1-imax, jmin, m.shape[0]-1-jmax))
    print('  ocean: %.1f%%   depth: %.0f-%.0f m'
          % (sm.sum()/sm.size*100, sh.min(), sh.max()))
    strip = lambda r: ''.join('O' if v == 1 else '.' for v in r)
    for e, v in [('S', sm[0, :]), ('N', sm[-1, :]),
                 ('W', sm[:, 0]), ('E', sm[:, -1])]:
        tag = ('all water -> OPEN'  if v.all()      else
               'ALL LAND -> CLOSE'  if v.sum() == 0 else
               'MIXED(%d land)' % int((v == 0).sum()))
        print('    %s edge: %3d/%3d ocean (%5.1f%%)  %s'
              % (e, int(v.sum()), len(v), v.sum()/len(v)*100, tag))
        print('       ', strip(v))
    print()

check('A) offshore only',        -21.0, -18.5, 20.0, 23.0)
check('B) upwelling front',      -20.0, -17.0, 19.0, 23.0)
check('C) front and shelf',      -21.0, -16.0, 18.0, 23.0)
PYEOF
```

```text
A) offshore only
  lon -21.0--18.5E lat 20.0-23.0N
  -> imin=12 imax=43 jmin=73 jmax=110
  parent cells: 32 x 38   child at 3x: 94 x 112
  margin to parent edge: W=12 E=37 S=73 N=12 cells
  ocean: 100.0%   depth: 1842-4362 m
    S edge:  32/ 32 ocean (100.0%)  all water -> OPEN
    N edge:  32/ 32 ocean (100.0%)  all water -> OPEN
    W edge:  38/ 38 ocean (100.0%)  all water -> OPEN
    E edge:  38/ 38 ocean (100.0%)  all water -> OPEN

B) upwelling front
  lon -20.0--17.0E lat 19.0-23.0N
  -> imin=24 imax=62 jmin=61 jmax=110
  parent cells: 39 x 50   child at 3x: 115 x 148
  margin to parent edge: W=24 E=18 S=61 N=12 cells
  ocean: 99.2%   depth: 50-4072 m
    S edge:  39/ 39 ocean (100.0%)  all water -> OPEN
    N edge:  39/ 39 ocean (100.0%)  all water -> OPEN
    W edge:  50/ 50 ocean (100.0%)  all water -> OPEN
    E edge:  41/ 50 ocean ( 82.0%)  MIXED(9 land)

C) front and shelf
  lon -21.0--16.0E lat 18.0-23.0N
  -> imin=12 imax=74 jmin=49 jmax=110
  parent cells: 63 x 62   child at 3x: 187 x 184
  margin to parent edge: W=12 E=6 S=49 N=12 cells
  ocean: 88.9%   depth: 50-4362 m
    S edge:  62/ 63 ocean ( 98.4%)  MIXED(1 land)
    N edge:  59/ 63 ocean ( 93.7%)  MIXED(4 land)
    W edge:  62/ 62 ocean (100.0%)  all water -> OPEN
    E edge:   0/ 62 ocean (  0.0%)  ALL LAND -> CLOSE
```

Box **C** is the one used in this chapter. Its east edge is solid land — the African
coast, correctly closed, exactly as the parent's own east boundary is. South and north
are mixed with land only at their eastern ends, where they meet that coast. West is
fully open ocean.

**Why not A or B?** Box A is entirely deep water: it would run cleanly and show almost
nothing, since open ocean at 2.9 km looks much like open ocean at 9 km. Box B reaches
the shelf but leaves 9 land cells in the *middle* of its east edge, which is the one
pattern to avoid — an open boundary slicing through a coastline. Box C pushes east
until that edge is uniformly land, and closes it.

**Reading the output:**

| Field | What it tells you |
|---|---|
| `imin/imax/jmin/jmax` | goes straight into the zoom `.ini` |
| `child at 3x` | the cost — cells scale as the square, and the child sub-steps 3× as well |
| `margin` | parent cells between the child and the parent's own edge; under 10 leaves AGRIF little room on an **open** edge, and doesn't matter on a closed one |
| `ocean %` | how much of the box is water — low means cells spent on land |
| `depth` | the child's `hmax`, and a warning of steep bathymetry |
| edge strips | the decisive check — see below |

### Reading the edges

An AGRIF child edge must be one of:

| Edge mask | Setting | Verdict |
|---|---|---|
| All water | **open** | parent supplies data across the whole edge |
| All land | **closed** | a coastal wall, which is true |
| Water then land, **contiguous** | open | an open boundary that terminates at a coast |

**Mixed edges are fine.** Box C's south and north boundaries carry land only at their
eastern ends, where they run into the coast, and the run below is stable with them.