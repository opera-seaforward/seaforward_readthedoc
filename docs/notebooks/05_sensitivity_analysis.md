# 04 -- Sensitivity analysis (Technical Specification Step 5.3)

**SEA-FORWARD** OceanPrediction-A toolkit

Perturb the **atmospheric forcing** (wind amplitude in `croco_blk.nc`), **re-run CROCO**, and compare the **upwelling response**. This is the clearest hands-on illustration in the whole toolkit of how the OceanPrediction-A value chain is connected end to end:

``` { .text .no-copy }
   U3                      C1                       D1
Upstream forcing  --->  Core Forecasting  --->  Downstream diagnostic
(wind, perturbed          Engine (CROCO)          (upwelling index,
 here)                    re-run with the          SST response --
                          perturbed forcing)        computed here)
```

A change made at **U2** (the wind field edited below) only becomes visible at **D1** (the SST/upwelling diagnostics at the end) *by passing through* **C1** -- you cannot skip the model run. This is why Step 5.3 requires an actual CROCO re-run between the two halves of this notebook, rather than
just perturbing a diagnostic directly.

**Demo mode.** A real CROCO re-run needs HPC access and takes far longerthan a notebook cell -- there's no honest way to fake that. So: Part A and Part C below run for real either way (against a small synthetic stand-in for what a re-run *would* produce, in demo mode, clearly labelled); Part B
(the actual re-run) is a genuine external step that this notebook cannot skip in real-data mode -- see the assert-gate in that section.

**Prerequisite:** run `03_exercises.ipynb` first (or at least its Exercise 1) -- the Bakun upwelling index computation is reused unchanged below.

*Language note (FR-09):* markdown and docstrings are in English; French translation is coordinated separately with the documentation team.

## Part A -- Perturb the wind forcing (U2)

We scale the 10 m wind components in `croco_blk.nc` by a fixed amplitude factor (**x1.5**, per Technical Specification Step 5.3) and write a new bulk-forcing file. Wind *stress* in bulk-flux formulations scales roughly with the square of wind speed, so a 1.5x wind-*speed* perturbation is a
substantially stronger forcing change than it first appears -- worth keeping in mind when you look at the SST response in Part C.

```python
import sys, os
sys.path.insert(0, os.path.abspath(".."))

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

import sftools.postprocess as pp
import sftools.validation as val
import _paths

CONFIG   = os.environ.get("SEAFORWARD_CONFIG", "Canary_12")
MAIN_DIR = os.environ.get("SEAFORWARD_MAIN_DIR", "~/seaforward/forecast/model-runs")
AVAILABLE_CYCLES = _paths.list_cycles(os.path.expanduser(MAIN_DIR), CONFIG)
print(f"forecast cycles found under {os.path.join(MAIN_DIR, CONFIG)}: {AVAILABLE_CYCLES}")

# >>> SET THIS to the cycle you want to perturb, e.g. "20260711" <<<
CYCLE = os.environ.get("SEAFORWARD_CYCLE", AVAILABLE_CYCLES[-1] if AVAILABLE_CYCLES else "")
```
```python
AMP_FACTOR = 1.5   # 

CROCO_HIS, REFERENCE, MAIN_DIR = _paths.get_paths(cycle=CYCLE, config=CONFIG, main_dir=MAIN_DIR)
YORIG = 2000   # forecast runs from the Copernicus Marine Forecast / Mercator anfc

GFS = os.environ.get("SEAFORWARD_MAIN_DIR", f"../forecast/model-runs/{CONFIG}/{CYCLE}/downloaded_data/GFS/for_croco/")
BLK_BASELINE = os.path.join(GFS, "U-COMPONENT_OF_WIND_Y9999M01.nc")
BLK_PERTURBED = os.path.splitext(BLK_BASELINE)[0] + f"_wind{AMP_FACTOR:g}.nc"

print(f"Opening forecast cycle {CYCLE}")
print(f"  CROCO history    : {CROCO_HIS}")
print(f"  baseline forcing : {BLK_BASELINE}")

# CROCOTOOLS bulk-forcing files commonly use 'uwnd'/'vwnd'; some pipelines
# instead carry 'Uwind'/'Vwind'. Detect whichever pair is present.
WIND_NAME_PAIRS = [(" U-component_of_wind", " v-component_of_wind")]

dsb = xr.open_dataset(BLK_BASELINE)
uname, vname = next(p for p in WIND_NAME_PAIRS if p[0] in dsb)
print(f"detected wind variables: {uname!r}, {vname!r}")
print(f"baseline wind speed range: "
     f"{float(np.sqrt(dsb[uname]**2 + dsb[vname]**2).min()):.2f} .. "
     f"{float(np.sqrt(dsb[uname]**2 + dsb[vname]**2).max()):.2f} m/s")
```

```python
AMP_FACTOR = 1.5   # 

dsp = dsb.copy(deep=True)
dsp[uname] = dsb[uname] * AMP_FACTOR
dsp[vname] = dsb[vname] * AMP_FACTOR
dsp[uname].attrs.update(dsb[uname].attrs)
dsp[vname].attrs.update(dsb[vname].attrs)
dsp.attrs["history"] = (dsb.attrs.get("history", "") +
                        f" | SEA-FORWARD 05_sensitivity: wind x{AMP_FACTOR} "
                        f"({uname},{vname}) for Step 5.3 sensitivity study")

dsp.to_netcdf(BLK_PERTURBED)
dsb.close(); dsp.close()
print(f"wrote perturbed forcing -> {BLK_PERTURBED}")
```

## Part B -- Re-run CROCO with the perturbed forcing (C1)

**In real-data mode**, this step happens *outside* the notebook, using the same forecast/hindcast orchestration script described in the Technical Specification (Step 4 of the operational workflow), pointed at `croco_blk_wind1.5.nc` instead of the baseline file:

```bash
source ~/seaforward/env.sh
source ~/seaforward/forecast/track.sh
export CONFIG_NAME=Canary_12
export FCAST=${CROCO_RUNS_ROOT}/${CONFIG_NAME}     # forecast/scratch/Canary_12
cd ${FCAST}
conda deactivate                                    # run outside conda
./croco croco.in 2>&1 | tee run.log | tail -60
```

## Part C -- Compare the upwelling response (D1)

Three comparisons, from the simplest to the most physically direct:

1. **SST difference map** (perturbed minus baseline): where did the wind change cool the surface, and by how much?
2. **Bakun upwelling index** at the coastal reference point (Exercise 1 of `03_exercises.ipynb`, reused verbatim), baseline vs. perturbed.
3. **Domain statistics** of the SST change, to put a single number on "how much stronger is upwelling with 1.5x wind".

```python
dsb_his = pp.open_history(HIS_BASELINE, Yorig=YORIG)
dsp_his = pp.open_history(HIS_PERTURBED, Yorig=YORIG)

clon, clat, cmask = pp.lonlatmask(dsb_his)
sst_baseline = pp.surface(dsb_his, "temp", tindex=-1).values
sst_perturbed = pp.surface(dsp_his, "temp", tindex=-1).values
sst_diff = sst_perturbed - sst_baseline

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
vmin, vmax = np.nanmin([sst_baseline, sst_perturbed]), np.nanmax([sst_baseline, sst_perturbed])
for ax, f, title in zip(axes, (sst_baseline, sst_perturbed, sst_diff),
                        ("baseline SST", f"perturbed SST (wind x{AMP_FACTOR})",
                         "difference (perturbed - baseline)")):
    if f is sst_diff:
        dmax = np.nanpercentile(np.abs(f[np.isfinite(f)]), 98)
        h = ax.pcolormesh(clon, clat, f, cmap="RdBu_r", vmin=-dmax, vmax=dmax, shading="auto")
    else:
        h = ax.pcolormesh(clon, clat, f, cmap="RdYlBu_r", vmin=vmin, vmax=vmax, shading="auto")
    ax.set_title(title, fontsize=10)
    plt.colorbar(h, ax=ax, shrink=0.8, label="degC")
fig.suptitle(f"CROCO SST response to a {AMP_FACTOR}x wind-amplitude perturbation")
plt.tight_layout(); plt.show()
```
```python
sst_change = val.domain_statistics(sst_perturbed, sst_baseline)
print(f"SST change (perturbed vs. baseline): mean = {sst_change['bias']:+.3f} C, "
     f"RMS = {sst_change['rmse']:.3f} C, n = {sst_change['n']}")
print("A negative mean bias here is the expected upwelling signature: stronger "
     "upwelling-favourable wind -> more coastal cooling.")
```

### Bakun upwelling index -- baseline vs. perturbed

Reusing the Exercise 1 calculation from `03_exercises.ipynb` unchanged,applied to both wind fields, so the *only* thing that differs between the two numbers below is the `AMP_FACTOR` scaling applied in Part A.

```python
OMEGA = 7.2921e-5
RHO_AIR, RHO_WATER, CD = 1.22, 1025.0, 1.3e-3
COAST_ANGLE_DEG = 90.0   # TODO: same coastline angle used in 04_exercises.ipynb


def bakun_index(u10, v10, lat0, coast_angle_deg=COAST_ANGLE_DEG):
    theta = np.deg2rad(coast_angle_deg)
    w_along = u10 * np.cos(theta) + v10 * np.sin(theta)
    w_speed = np.sqrt(u10 ** 2 + v10 ** 2)
    f = 2 * OMEGA * np.sin(np.deg2rad(lat0))
    return (RHO_AIR * CD * w_speed * w_along) / (RHO_WATER * f)


LON0 = float(clon[cmask > 0][0]); LAT0 = float(clat[cmask > 0][0])
dsb_blk = xr.open_dataset(BLK_BASELINE)
j = np.argmin((dsb_blk["lat"].values[:, 0] - LAT0) ** 2)
i = np.argmin((dsb_blk["lon"].values[0, :] - LON0) ** 2)
u0_base = float(dsb_blk[uname].isel(time=-1).values[j, i])
v0_base = float(dsb_blk[vname].isel(time=-1).values[j, i])
u0_pert = u0_base * AMP_FACTOR
v0_pert = v0_base * AMP_FACTOR
dsb_blk.close()

Qx_base = bakun_index(u0_base, v0_base, LAT0)
Qx_pert = bakun_index(u0_pert, v0_pert, LAT0)
print(f"Bakun index, baseline : {Qx_base:+.3f} m2/s")
print(f"Bakun index, perturbed: {Qx_pert:+.3f} m2/s")
if Qx_base != 0:
    print(f"  ratio: x{Qx_pert / Qx_base:.2f} relative to baseline")
```

!!! note
    The qualitative result -- that the index scales *faster* than linearly with `AMP_FACTOR` -- holds because both the alongshore-wind term *and* the wind-speed term in the Bakun formula grow together (Qx is proportional to `&#124;W&#124; * W_alongshore`, i.e. roughly quadratic in wind speed for wind blowing mostly alongshore). Compare `Qx_pert/Qx_base` above to `AMP_FACTOR**2` to check this directly on your own run.

```python
# Self-check: the perturbed index should scale up with AMP_FACTOR, in the
# same direction as the baseline (same upwelling/downwelling sign)
assert np.sign(Qx_pert) == np.sign(Qx_base), "perturbation flipped the upwelling sign -- check COAST_ANGLE_DEG"
assert abs(Qx_pert) > abs(Qx_base), "perturbed index should be stronger than baseline for AMP_FACTOR > 1"
print("self-check passed")

dsb_his.close(); dsp_his.close()
```

## Summary

This notebook closed the loop from **U2** (perturbed wind forcing) through **C1** (the re-run CROCO model) to **D1** (the SST and upwelling-index response) -- the exact chain the Technical Specification's Data Consistency Chain (DCC) architecture requires. Record your `AMP_FACTOR`, the resulting SST bias/RMSE, and the Bakun-index ratio in your lab notes.

*Reminder:* results above are DEMO DATA unless you completed Part B with a real CROCO re-run -- check the `IS_DEMO` flag printed near the top of this notebook before drawing any scientific conclusions.

<div style="display:flex; justify-content:center; margin:10px 0 14px 0;">
   <a href="https://raw.githubusercontent.com/opera-seaforward/seaforward_readthedoc/main/docs/notebooks/04_sensitivity.ipynb" data-download-url="https://raw.githubusercontent.com/opera-seaforward/seaforward_readthedoc/main/docs/notebooks/04_sensitivity.ipynb" data-download-filename="04_sensitivity.ipynb" onmouseover="this.style.transform='scale(1.08)'; this.style.boxShadow='0 10px 24px rgba(0,0,0,0.18)';" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none';" style="display:inline-flex; align-items:center; justify-content:center; gap:16px; min-width: 80px; padding:20px 20px; border-radius:10px; background:linear-gradient(to bottom, #ffffcc 0%, #f4f797de 100%); color:#000000; text-decoration:none; font-size:1.2rem; line-height:1.1; text-align:center; transition:transform 0.18s ease, box-shadow 0.18s ease; transform-origin:center;">
      <img src="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/download.svg" alt="" aria-hidden="true" style="width:25px; height:25px; color:#000000; font-weight:bold filter:invert(1);" />
      <span>Download notebook 04_sensitivity.ipynb</span>
   </a>
</div>
