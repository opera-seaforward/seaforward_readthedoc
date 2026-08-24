# ======================================================================
# SEA-FORWARD — region build/inspect snippets (cell style)
# Reusable per region. Set GRD to the region's croco_grd.nc, then run a cell.
# ======================================================================

# %% [cell 0] — point at a region grid
GRD = "/home/btchonang/seaforward/forecast/scratch/IGOG_12/CROCO_FILES/croco_grd.nc"
TITLE = "Gulf of Guinea — IGOG 1/12"


# %% [cell 1] — grid size (LLm0 / MMm0 for param.h)
import xarray as xr
g = xr.open_dataset(GRD)
xi, eta = g.sizes["xi_rho"], g.sizes["eta_rho"]
print(f"xi_rho={xi}  eta_rho={eta}   ->  LLm0={xi-2}  MMm0={eta-2}")
print(f"depth h: {float(g.h.min()):.0f} .. {float(g.h.max()):.0f} m")


# %% [cell 2] — boundary map (which edges are ocean vs coast)
import xarray as xr
g = xr.open_dataset(GRD); m = g.mask_rho.values
strip = lambda r: "".join("O" if v == 1 else "." for v in r)
print("south:", int(m[0, :].sum()), "/", m.shape[1], "  W", strip(m[0, :]), "E")
print("north:", int(m[-1, :].sum()), "/", m.shape[1], "  W", strip(m[-1, :]), "E")
print("west :", int(m[:, 0].sum()), "/", m.shape[0], "  S", strip(m[:, 0]), "N")
print("east :", int(m[:, -1].sum()), "/", m.shape[0], "  S", strip(m[:, -1]), "N")


# %% [cell 3] — derive obc_dict from the mask (open if edge is mostly ocean)
import xarray as xr
g = xr.open_dataset(GRD); m = g.mask_rho.values
for name, e in [("south", m[0, :]), ("north", m[-1, :]),
                ("west", m[:, 0]), ("east", m[:, -1])]:
    frac = e.sum() / len(e)
    print(f"{name:6s}: {int(e.sum()):3d}/{len(e):3d} = {frac*100:5.1f}% ocean "
          f"-> {'OPEN (1)' if frac > 0.5 else 'closed (0)'}")
print()
print("obc_dict = dict(south=%d, west=%d, east=%d, north=%d)" % (
    1 if m[0, :].sum() / m.shape[1] > 0.5 else 0,
    1 if m[:, 0].sum() / m.shape[0] > 0.5 else 0,
    1 if m[:, -1].sum() / m.shape[0] > 0.5 else 0,
    1 if m[-1, :].sum() / m.shape[1] > 0.5 else 0,
))


# %% [cell 4] — region portrait (grid + bathymetry) for the Doc 07 gallery
#     run from ~/seaforward so sftools imports
import sftools.plotting as pl
pl.grid_bathy_map(GRD, title=TITLE, coastline=True, mesh_stride=2,
                  out="/tmp/region_portrait.png")
print("saved /tmp/region_portrait.png")


# %% [cell 5] — a result figure (SST) once a forecast his exists
#     for the gallery card's "region in action" panel
import sftools.postprocess as pp, sftools.plotting as pl
HIS = "/home/btchonang/seaforward/forecast/model-runs/IGOG_12/<DATE>/fcst/CROCO_FILES/croco_his.nc"
ds  = pp.open_history(HIS, Yorig=2000)                  # open first (field_map takes a dataset)
sst = pp.field_map(ds, var="temp", tindex=-1, level=-1) # last record, surface σ-level
pl.plot_map(sst, cmap="RdYlBu_r", out="/tmp/region_sst.png")
print("saved /tmp/region_sst.png")
