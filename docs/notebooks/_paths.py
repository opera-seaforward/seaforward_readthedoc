"""
notebooks/_paths.py — real-data path helpers for 02_validation.ipynb.

FORECAST ONLY, REAL DATA ONLY (no synthetic/demo fallback): every forecast
run lives in a cycle directory named YYYYMMDD (e.g. "20260711" for the
5-day forecast cycle covering 11-15 July 2026), sibling to every other
cycle under one config directory:

    <main_dir>/<config>/<cycle>/fcst/CROCO_FILES/croco_his.nc                  (CROCO forecast output)
    <main_dir>/<config>/<cycle>/downloaded_data/MERCATOR/MERCATOR_<cycle>_00.nc (Copernicus Marine Forecast, combined)
    <main_dir>/<config>/<cycle>/downloaded_data/{OSTIA,ODYSSEA,INSITU}/...      (validation-only, this notebook downloads here)

There can be several cycle directories at once (one per forecast run) --
list_cycles() enumerates them and the caller/user picks one explicitly via
CYCLE; nothing here auto-selects a cycle.
"""
import os
import re

_CYCLE_RE = re.compile(r"^\d{8}$")


def cycle_dir(main_dir, config, cycle):
    return os.path.join(main_dir, config, cycle)


def croco_his_path(main_dir, config, cycle):
    """CROCO forecast history file for this cycle (<cycle>/fcst/CROCO_FILES/croco_his.nc)."""
    return os.path.join(cycle_dir(main_dir, config, cycle), "fcst",
                        "CROCO_FILES", "croco_his.nc")


def mercator_reference_path(main_dir, config, cycle):
    """The combined Copernicus Marine Forecast file (thetao/so/uo/vo/zos all
    in one file, as sftools.validation.load_parent expects) for this
    forecast cycle -- MERCATOR_<cycle>_00.nc under downloaded_data/MERCATOR/.
    Built by sftools.download.cmems.download_mercator_ops() if not already
    present (see the notebook's download section).
    """
    return os.path.join(cycle_dir(main_dir, config, cycle),
                        "downloaded_data", "MERCATOR", f"MERCATOR_{cycle}_00.nc")


def satellite_dir(main_dir, config, cycle, product):
    """product: 'OSTIA' or 'ODYSSEA'. Not part of the run pipeline's own
    downloads -- sftools.download.cmems.download_satellite_sst() fetches
    into this per-cycle directory the same way GFS/MERCATOR already are, so
    the validation notebook's satellite comparison follows the same
    one-cycle-one-place convention as everything else."""
    return os.path.join(cycle_dir(main_dir, config, cycle), "downloaded_data", product)


def insitu_dir(main_dir, config, cycle):
    return os.path.join(cycle_dir(main_dir, config, cycle), "downloaded_data", "INSITU")


def get_validation_dir(main_dir, config, cycle, create=True):
    """The validation output directory for this cycle: a SIBLING of the
    cycle directories (main_dir/config/validation_<cycle>), not nested
    inside one -- so it survives/organises independently of a given fcst
    run directory being cleaned up or re-run."""
    vdir = os.path.join(main_dir, config, f"validation_{cycle}")
    if create:
        os.makedirs(vdir, exist_ok=True)
    return vdir


def list_cycles(main_dir, config):
    """List every forecast cycle available under main_dir/config, i.e.
    every YYYYMMDD subdirectory that actually has a CROCO history file --
    sorted oldest to newest. Returns [] (not an error) if main_dir/config
    doesn't exist yet or has no runnable cycle.
    """
    base = os.path.join(main_dir, config)
    if not os.path.isdir(base):
        return []
    cycles = []
    for name in sorted(os.listdir(base)):
        if _CYCLE_RE.match(name) and os.path.exists(croco_his_path(main_dir, config, name)):
            cycles.append(name)
    return sorted(cycles)


def get_paths(cycle, config="Canary_12", main_dir=None):
    """Return (croco_his, reference) for one real FORECAST cycle. No demo
    fallback: raises FileNotFoundError with a helpful listing of the
    cycles that ARE available if croco_his.nc isn't there.

    cycle    : the cycle directory name, e.g. "20260711". Required -- the
               user picks which cycle to validate (see list_cycles()).
    config   : the model configuration directory name (e.g. "Canary_12").
    main_dir : the directory that directly contains <config>/ (i.e. the
               parent of every cycle directory). Defaults to
               "~/seaforward/forecast/model-runs".
    """
    if main_dir is None:
        main_dir = os.environ.get(
            "SEAFORWARD_MAIN_DIR",
            os.path.expanduser("~/seaforward/forecast/model-runs"))
    main_dir = os.path.expanduser(main_dir)

    if not cycle:
        available = list_cycles(main_dir, config)
        raise ValueError(
            "CYCLE is not set -- pick which forecast cycle to validate.\n"
            f"Available cycles under {os.path.join(main_dir, config)}: "
            f"{available if available else '(none found)'}")

    croco_his = croco_his_path(main_dir, config, cycle)
    if not os.path.exists(croco_his):
        available = list_cycles(main_dir, config)
        raise FileNotFoundError(
            f"No CROCO history file for cycle {cycle!r} at {croco_his}.\n"
            f"Available cycles under {os.path.join(main_dir, config)}: "
            f"{available if available else '(none found)'}")

    reference = mercator_reference_path(main_dir, config, cycle)
    return croco_his, reference, main_dir
