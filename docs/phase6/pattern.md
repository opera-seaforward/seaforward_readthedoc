Building any region is the same recipe with a few swapped values:

| Always changes per region | Always the same |
|---|---|
| Box (lon/lat extent) | Vertical grid (θ_s=7, θ_b=2, hc=200, N=50) |
| Grid size (LLm0, MMm0) | The four config files' structure |
| Open/closed boundaries, read from the mask | The compile — `jobcomp`, `opt_seq` NetCDF |
| `FIX_GFS_LON`, by hemisphere | The forecast driver machinery |
| Physical regime — upwelling, equatorial, western boundary current | `make_ini`, `make_bry`, the `croco.in` patching |

So a new region is: pick the box, build the grid, read the boundaries, set
`FIX_GFS_LON`, copy and edit the four config files, compile, run. Each card in this
chapter is that process frozen at the "here's the result" stage.

## Adding a card

Copy this template, fill it in from your build, and drop the portrait into
`docs/img/` as `<config>_portrait.png`:

```markdown
<one-line description of the region>

![<CONFIG> grid and bathymetry](../img/<config>_portrait.png)

| | |
|---|---|
| **Box** | <lon/lat extent> |
| **Resolution** | 1/12°, 50 σ-levels |
| **Grid** | <xi> × <eta> (LLm0=<xi−2>, MMm0=<eta−2>) |
| **Boundaries** | <which open, which closed, and why> |
| **Hemisphere** | <Eastern → FIX_GFS_LON=0 / Western → FIX_GFS_LON=1> |
| **Distinctive** | <what makes this region physically interesting> |
| **Build** | `make_grid_config.py "<CONFIG>" <lonmin> <lonmax> <latmin> <latmax> 1/12 1/12` |

**Physical notes.** <the dominant dynamics — currents, upwelling, retroflection…>

**Per-region gotchas.** <CFL and timestep, steep bathymetry, hemisphere, straddling 0°…>
```

The numbers all come from the grid file:

```bash
python3 -c "
import xarray as xr
g = xr.open_dataset('forecast/scratch/<CONFIG>/CROCO_FILES/croco_grd.nc')
m = g.mask_rho.values
print('grid %d x %d' % (g.sizes['xi_rho'], g.sizes['eta_rho']))
print('lon %.2f..%.2f  lat %.2f..%.2f' % (float(g.lon_rho.min()), float(g.lon_rho.max()),
                                          float(g.lat_rho.min()), float(g.lat_rho.max())))
for n, r in [('south', m[0,:]), ('north', m[-1,:]), ('west', m[:,0]), ('east', m[:,-1])]:
    print('%-6s %d/%d ocean' % (n, int(r.sum()), len(r)))
"
```