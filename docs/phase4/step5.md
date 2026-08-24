The hindcast atmosphere subcommand downloads GFS from CDS **and** converts it to
CROCO online-forcing format in one command:

```bash
cd ${SEAFORWARD}
python seaforward.py download_atmosphere_hindcast \
    --domain="${GFS_BOX}" \
    --month_start 2025-12 --month_end 2026-01 \
    --outputDir ${HCAST}/downloaded_data/GFS
```

**What it does (two internal stages):**

1. **request** — pulls raw GFS (10 variables: lsm, sst, tp, strd, ssr, t2m, q, u10, v10, msl) from CDS into `GFS/raw/`. A 2° margin is added around the box.
2. **convert** — reshapes raw GFS into CROCO online forcing in `GFS/for_croco/`, applying unit conversions (precip → kg m⁻² s⁻¹, radiation → W m⁻²).

!!! note
    **CDS queues.** GFS requests queue on CDS's servers; a month is usually a few minutes but can be longer under load. The command handles request→convert automatically.

!!! check
    ✅ **CHECK** — 10 converted files per month in `for_croco/`, named `<VAR>_Y<year>M<month>.nc`:
    ```bash
    ls ${HCAST}/downloaded_data/GFS/for_croco/ | sort
    ```

You want, per month: `T2M_ Q_ TP_ SSR_ STRD_ U10M_ V10M_ msl_ SST_ LSM_` with the
`_Y2025M12.nc` / `_Y2026M01.nc` suffix.

!!! warning
    ⚠️ **WATCH — zero-pad the month (`M01`, not `M1`).** CROCO's GFS online reader expects a **two-digit** month for Jan–Sep (`M01`…`M09`) by default. The convert writes `str(imonth).zfill(2)` so single-digit months come out padded. If you ever see files like `T2M_Y2026M1.nc` (unpadded), rename them: `for f in *Y2026M1.nc; do mv "$f" "${f%Y2026M1.nc}Y2026M01.nc"; done` (Months ≥10 are always two-digit, so December `M12` is fine.)

!!! note
    **Skip-existing.** The GFS request re-downloads unless the raw files already exist; the wrapper regenerates `GFS_crocotools_param.py` from your args each run (so you never hand-edit that param file).