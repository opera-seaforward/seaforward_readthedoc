"""
notebooks/_demo_data.py — SEA-FORWARD demo/fallback data.

DCC processes: supports D1 (Downstream Applications / notebooks).

Not a deliverable notebook itself — a small shared helper the four notebooks
import so they can execute end-to-end (QA requirement: "all four notebooks
execute without errors from a fresh kernel restart and run-all", Testing and
Validation Plan §9.1) even before the real D10.2 (Forcing Data Archive) and
D10.3 (Reference Results Dataset) are downloaded from Zenodo.

Behaviour
---------
`get_paths()` first looks for real data at the configured paths (see
DEFAULT_* below, overridable via environment variables so CI/pilot users can
point at their own download location without editing notebook cells). If the
real CROCO history / reference (GLORYS-like) files aren't there, it builds a
small synthetic stand-in with the SAME schema real files have (verified
against sftools/postprocess.py's and sftools/validation.py's actual field
names/shapes) — clearly labelled DEMO DATA in every notebook that uses it, so
nobody mistakes a demo run for a validated scientific result.

This is deliberately not "the model" — it's a stand-in so the toolkit is
runnable and testable before real CROCO/GLORYS files exist locally in a given
environment.
"""
from __future__ import annotations
import os
import numpy as np
import xarray as xr

import sftools.postprocess as pp

# ------------------------------------------------------------------------
# Where real data is expected. Overridable via environment variables so
# this doesn't need editing per machine (DevOps Eng., install docs D10.4).
# ------------------------------------------------------------------------
DEFAULT_CROCO_HIS = os.environ.get(
    "SEAFORWARD_CROCO_HIS",
    "../hindcast/model-runs/Canary_12/20251225/hcast/CROCO_FILES/croco_his.nc")
DEFAULT_GLORYS = os.environ.get(
    "SEAFORWARD_GLORYS", "../hindcast/downloaded_data/GLORYS/reference.nc")
DEMO_DIR = os.environ.get("SEAFORWARD_DEMO_DIR", "./_demo_cache")


def _make_synthetic_croco(path, nt=6, neta=40, nxi=48, nz=10,
                          lon0=-16.5, lat0=27.0, dlonlat=0.04,
                          Yorig=2025, seed=0, intensity=1.0):
    """A small, schema-correct CROCO-history-like file with an idealised
    coastal upwelling signature: cooler SST and an equatorward coastal jet
    near the eastern (coastal) boundary, so the guided exercises (upwelling
    index, coastal jet, MLD) and the eddy-detection exercise all have
    something real to find. NOT a physical CROCO run — a teaching stand-in.

    intensity : multiplies the coastal-cooling/jet strength. Used by
    get_sensitivity_paths() to build a "perturbed" demo run (intensity>1)
    that stands in for what a real re-run with stronger wind forcing would
    produce, so 04_sensitivity.ipynb's Part C comparison code has something
    real to compare even before an actual CROCO re-run has been done.
    """
    rng = np.random.default_rng(seed)
    lat_rho = lat0 + dlonlat * np.arange(neta)
    lon_rho = lon0 + dlonlat * np.arange(nxi)
    LON, LAT = np.meshgrid(lon_rho, lat_rho)

    mask_rho = np.ones((neta, nxi))
    # a simple coastline: land along the eastern edge, tapering
    coast_i = nxi - 4
    for j in range(neta):
        mask_rho[j, coast_i + (j % 3 >= 2):] = 0.0

    h = np.clip(200 + 15 * (coast_i - np.arange(nxi))[None, :] * np.ones((neta, 1)), 30, 2000)
    angle = np.zeros((neta, nxi))
    hc, theta_s, theta_b, Vtransform, N = 10.0, 6.0, 3.0, 2, nz

    dist_to_coast = np.clip((coast_i - np.arange(nxi)), 0, None)[None, :] * np.ones((neta, 1))
    # coastal upwelling: SST drops near the coast, deepens/strengthens with
    # a mild time evolution so the sensitivity notebook has something to
    # compare before/after a stronger wind
    zeta = 0.02 * np.sin(np.linspace(0, 2 * np.pi, nxi))[None, None, :] * np.ones((nt, neta, 1))
    z0 = pp.z_levels(h, zeta[0], theta_s, theta_b, hc, N, vtransform=Vtransform)[0]
    depth_pos = -z0

    temp = np.empty((nt, N, neta, nxi))
    salt = np.empty((nt, N, neta, nxi))
    u = np.empty((nt, N, neta, nxi - 1))
    v = np.empty((nt, N, neta - 1, nxi))
    for t in range(nt):
        upwelling_strength = intensity * (1.0 + 0.15 * t / max(nt - 1, 1))   # slow intensification
        coastal_cool = -3.0 * np.exp(-dist_to_coast / 8.0) * upwelling_strength
        temp[t] = (18.0 - 0.03 * depth_pos + coastal_cool[None, :, :]
                  + 0.1 * rng.standard_normal((N, neta, nxi)))
        salt[t] = 36.2 + 0.05 * np.exp(-dist_to_coast[None, :, :] / 10.0)
        # equatorward (southward, negative v) coastal jet just offshore of the coast
        jet = -0.3 * np.exp(-((dist_to_coast - 3) ** 2) / (2 * 2.0 ** 2)) * upwelling_strength
        v[t] = np.broadcast_to(jet[:, :nxi], (N, neta, nxi))[:, :neta - 1, :]
        u[t] = 0.03 * rng.standard_normal((N, neta, nxi - 1))
        # a synthetic mesoscale eddy pair offshore, for the eddy-detection exercise
        for (cj, ci, amp) in [(neta // 3, nxi // 3, +0.10), (2 * neta // 3, nxi // 4, -0.08)]:
            r2 = (np.arange(neta)[:, None] - cj) ** 2 + (np.arange(nxi)[None, :] - ci) ** 2
            zeta[t] += amp * np.exp(-r2 / (2 * 4.0 ** 2))

    time_seconds = np.arange(nt) * 24 * 3600.0

    ds = xr.Dataset(
        data_vars=dict(
            zeta=(("time", "eta_rho", "xi_rho"), zeta),
            temp=(("time", "s_rho", "eta_rho", "xi_rho"), temp),
            salt=(("time", "s_rho", "eta_rho", "xi_rho"), salt),
            u=(("time", "s_rho", "eta_rho", "xi_u"), u),
            v=(("time", "s_rho", "eta_v", "xi_rho"), v),
            h=(("eta_rho", "xi_rho"), h),
            angle=(("eta_rho", "xi_rho"), angle),
            mask_rho=(("eta_rho", "xi_rho"), mask_rho),
            hc=((), hc), Vtransform=((), Vtransform),
        ),
        coords=dict(
            lon_rho=(("eta_rho", "xi_rho"), LON),
            lat_rho=(("eta_rho", "xi_rho"), LAT),
            time=("time", time_seconds,
                 {"units": f"seconds since {Yorig}-12-25 00:00:00"}),
        ),
        attrs=dict(theta_s=theta_s, theta_b=theta_b,
                  title="SEA-FORWARD DEMO DATA — synthetic, not a physical CROCO run",
                  source="notebooks/_demo_data.py"),
    )
    ds.to_netcdf(path)
    return Yorig


def _make_synthetic_glorys(path, croco_meta, offset_temp=0.3, offset_ssh=0.01):
    """A GLORYS12V1-like 'reference' file matching sftools.validation's
    PARENT_VARS naming, built as the demo CROCO field plus a small known
    offset — so the validation notebook's bias/RMSE numbers are meaningful
    (checkable) rather than arbitrary."""
    lon0 = croco_meta["lon0"]; lat0 = croco_meta["lat0"]
    dlonlat = croco_meta["dlonlat"]
    nlon, nlat = croco_meta["nxi"] + 6, croco_meta["neta"] + 6
    lon = lon0 - 0.1 + dlonlat * np.arange(nlon)
    lat = lat0 - 0.1 + dlonlat * np.arange(nlat)
    depth = np.array([0, 10, 30, 50, 100, 200, 500.0])

    dist = np.abs(np.arange(nlon)[None, :] - (nlon - 8))
    coastal_cool = -3.0 * np.exp(-np.clip(dist, 0, None) / 8.0)
    thetao = (18.0 + offset_temp - 0.03 * depth[None, :, None, None]
             + coastal_cool[None, None, :, :]
             + np.zeros((1, len(depth), nlat, nlon)))
    so = np.full((1, len(depth), nlat, nlon), 36.2)
    uo = np.full((1, len(depth), nlat, nlon), 0.02)
    vo = np.full((1, len(depth), nlat, nlon), -0.05)
    zos_1d = 0.02 * np.sin(np.linspace(0, 2 * np.pi, nlon)) + offset_ssh   # (nlon,)
    zos = np.broadcast_to(zos_1d[None, None, :], (1, nlat, nlon)).copy()   # (time, lat, lon)

    ds = xr.Dataset(
        data_vars=dict(
            thetao=(("time", "depth", "latitude", "longitude"), thetao),
            so=(("time", "depth", "latitude", "longitude"), so),
            uo=(("time", "depth", "latitude", "longitude"), uo),
            vo=(("time", "depth", "latitude", "longitude"), vo),
            zos=(("time", "latitude", "longitude"), zos),
        ),
        coords=dict(longitude=lon, latitude=lat, depth=depth,
                   time=("time", np.array([np.datetime64(
                       f"{croco_meta['Yorig']}-12-25T12:00:00")]))),
        attrs=dict(title="SEA-FORWARD DEMO DATA — synthetic GLORYS12V1 stand-in"),
    )
    ds.to_netcdf(path)


def make_synthetic_wind(lon0=-16.5, lat0=27.0, dlonlat=0.04, neta=40, nxi=48,
                        speed=8.0, seed=0):
    """An idealised upwelling-favourable 10 m wind field: blowing due south
    (v10 = -speed, u10 ~ 0) everywhere, i.e. parallel to a north-south
    coastline (COAST_ANGLE_DEG = 0 in the exercises' convention) — a
    deliberately simple demo case so the Bakun-index exercise gives a clean,
    interpretable sign (upwelling-favourable) without needing real ERA5
    files or the true local coastline orientation. NOT a real wind field.
    """
    rng = np.random.default_rng(seed)
    lat = lat0 + dlonlat * np.arange(neta)
    lon = lon0 + dlonlat * np.arange(nxi)
    lon2d, lat2d = np.meshgrid(lon, lat)
    u10 = 0.5 * rng.standard_normal(lon2d.shape)         # small cross-shore noise
    v10 = np.full(lon2d.shape, -speed) + 0.5 * rng.standard_normal(lon2d.shape)
    return lon2d, lat2d, u10, v10


def _make_synthetic_blk(path, lon2d, lat2d, u10, v10, Yorig, nt=2):
    """A minimal croco_blk.nc-like bulk-forcing stand-in with uwnd/vwnd on
    (time, eta, xi), matching the WIND_NAME_PAIRS convention used in
    04_sensitivity.ipynb Part A."""
    uwnd = np.broadcast_to(u10, (nt,) + u10.shape).copy()
    vwnd = np.broadcast_to(v10, (nt,) + v10.shape).copy()
    ds = xr.Dataset(
        data_vars=dict(
            uwnd=(("time", "eta_rho", "xi_rho"), uwnd),
            vwnd=(("time", "eta_rho", "xi_rho"), vwnd),
        ),
        coords=dict(
            lon=(("eta_rho", "xi_rho"), lon2d), lat=(("eta_rho", "xi_rho"), lat2d),
            time=("time", np.arange(nt) * 6 * 3600.0,
                 {"units": f"seconds since {Yorig}-12-25 00:00:00"}),
        ),
        attrs=dict(title="SEA-FORWARD DEMO DATA — synthetic bulk-forcing stand-in"),
    )
    ds.to_netcdf(path)


def get_sensitivity_paths(amp_factor=1.5, force_demo=False):
    """Paths (+ demo status) for 04_sensitivity.ipynb.

    Real-data mode (has_real): returns the configured baseline blk/history
    paths and None for the perturbed ones — Part A writes the perturbed blk
    file for real, and Part B's external CROCO re-run is a genuine,
    unavoidable manual step (faking "what a re-run would produce" would be
    scientifically dishonest, unlike the validation/exercise notebooks
    where a synthetic stand-in is a fair substitute for demonstrating the
    *analysis* code).

    Demo mode: ALSO auto-generates a synthetic "perturbed" CROCO history
    file (stronger coastal cooling, via the `intensity` parameter of
    _make_synthetic_croco) standing in for what a real re-run with
    `amp_factor` x wind WOULD produce, wind-stress-like (~amp_factor**1.3,
    reflecting that stress grows faster than linearly with wind speed in a
    quadratic bulk formula) — so Part C's comparison code is fully
    exercised even without HPC access, clearly labelled as DEMO DATA
    throughout.
    """
    croco_his, glorys, yorig, is_demo = get_paths(force_demo=force_demo)
    if not is_demo:
        return dict(blk_baseline=None, blk_perturbed=None,
                   his_baseline=croco_his, his_perturbed=None,
                   Yorig=yorig, is_demo=False)

    os.makedirs(DEMO_DIR, exist_ok=True)
    blk_baseline = os.path.join(DEMO_DIR, "croco_blk_demo.nc")
    his_perturbed = os.path.join(DEMO_DIR, f"croco_his_demo_wind{amp_factor:g}.nc")

    lon2d, lat2d, u10, v10 = make_synthetic_wind()
    if not os.path.exists(blk_baseline):
        _make_synthetic_blk(blk_baseline, lon2d, lat2d, u10, v10, yorig)
    if not os.path.exists(his_perturbed):
        # wind-stress-like scaling (stress ~ speed^2 in a quadratic bulk
        # formula) rather than a flat amp_factor, to match the physical
        # point made in the notebook's own Part A markdown
        _make_synthetic_croco(his_perturbed, Yorig=yorig,
                              intensity=amp_factor ** 1.3)

    return dict(blk_baseline=blk_baseline, blk_perturbed=None,
               his_baseline=croco_his, his_perturbed=his_perturbed,
               Yorig=yorig, is_demo=True)
    """Return (croco_his, glorys, Yorig, is_demo).

    Yorig is None for real data (files are expected to carry proper CF time
    units and decode without an override) and the synthetic file's actual
    reference year for demo data. Builds & caches synthetic demo files under
    DEMO_DIR the first time real data isn't found; reuses them on subsequent
    runs (fast kernel restarts) — delete DEMO_DIR to force a rebuild after a
    change to this module.
    """
    has_real = (not force_demo
               and os.path.exists(DEFAULT_CROCO_HIS)
               and os.path.exists(DEFAULT_GLORYS))
    if has_real:
        return DEFAULT_CROCO_HIS, DEFAULT_GLORYS, None, False

    os.makedirs(DEMO_DIR, exist_ok=True)
    croco_path = os.path.join(DEMO_DIR, "croco_his_demo.nc")
    glorys_path = os.path.join(DEMO_DIR, "glorys_demo.nc")
    meta_path = os.path.join(DEMO_DIR, "Yorig.txt")

    if not (os.path.exists(croco_path) and os.path.exists(glorys_path)):
        Yorig = _make_synthetic_croco(croco_path)
        with open(meta_path, "w") as f:
            f.write(str(Yorig))
        ds = xr.open_dataset(croco_path)
        lon2d = ds["lon_rho"].values; lat2d = ds["lat_rho"].values
        meta = dict(lon0=float(lon2d[0, 0]), lat0=float(lat2d[0, 0]),
                   dlonlat=float(lon2d[0, 1] - lon2d[0, 0]),
                   nxi=ds.sizes["xi_rho"], neta=ds.sizes["eta_rho"], Yorig=Yorig)
        ds.close()
        _make_synthetic_glorys(glorys_path, meta)

    with open(meta_path) as f:
        Yorig = int(f.read().strip())
    return croco_path, glorys_path, Yorig, True
