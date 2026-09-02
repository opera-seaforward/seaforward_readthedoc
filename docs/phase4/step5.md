The hindcast atmosphere subcommand downloads ERA5 from CDS **and** converts it to
CROCO online-forcing format in one command:

```bash
cd ${SEAFORWARD}
python seaforward.py download_atmosphere_hindcast \
    --domain="${ERA5_BOX}" \
    --month_start 2025-12 --month_end 2026-01 \
    --outputDir ${HCAST}/downloaded_data/ERA5
```

**What it does, in two internal stages:**

1. **request** — pulls raw ERA5 (10 variables: `lsm`, `sst`, `tp`, `strd`, `ssr`, `t2m`, `q`, `u10`, `v10`, `msl`) from CDS into `ERA5/raw/`. A 2° margin is added around the box, which is why this command takes the **grid box** rather than the padded `EXTENTS`.
2. **convert** — reshapes the raw fields into CROCO online forcing in `ERA5/for_croco/`, applying unit conversions (precipitation → kg m⁻² s⁻¹, radiation → W m⁻²).

!!! note
    **CDS queues.** ERA5 requests queue on the CDS servers; a month is usually a few minutes but can be much longer under load. The command handles request → convert automatically, so start it and leave it.

!!! check
    Ten converted files per month in `for_croco/`, named `<VAR>_Y<year>M<month>.nc`:
    ```bash
    ls ${HCAST}/downloaded_data/ERA5/for_croco/ | sort
    ls ${HCAST}/downloaded_data/ERA5/for_croco/*.nc | wc -l    # 10 per month
    ```

    Per month you want `T2M`, `Q`, `TP`, `SSR`, `STRD`, `U10M`, `V10M`, `MSL`, `SST` and `LSM`, each with the `_Y2025M12.nc` or `_Y2026M01.nc` suffix.

!!! warning
    **Zero-pad the month — `M01`, not `M1`.** CROCO's online reader expects a two-digit month for January to September. The converter writes `str(imonth).zfill(2)`, so they come out padded. If you ever see unpadded files, rename them:
    ```bash
    for f in *Y2026M1.nc; do mv "$f" "${f%Y2026M1.nc}Y2026M01.nc"; done
    ```
    Months from October on are always two digits, so December's `M12` is never affected.

!!! note
    **Re-running is safe.** The request skips raw files that already exist, and the wrapper regenerates `era5_crocotools_param.py` from your arguments each run — so you never hand-edit that parameter file.