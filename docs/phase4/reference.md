```bash
source ~/seaforward/env.sh
source ~/seaforward/hindcast/track.sh
conda activate seaforward

# data (GLORYS + GFS) for the period + neighbour months
python seaforward.py download_ocean_hindcast --domain="-23.5,-14.0,12.5,25.5" \
    --month_start 2025-12 --month_end 2026-01 \
    --product_id cmems_mod_glo_phy_my_0.083deg_P1D-m --outputDir ${HCAST}/downloaded_data/GLORYS
python seaforward.py download_atmosphere_hindcast --domain="-22,-15.5,14,24" \
    --month_start 2025-12 --month_end 2026-01 --outputDir ${HCAST}/downloaded_data/GFS

# config: reuse Phase 2, but inputdata='mercator', ERA_ECMWF defined, Yorig=1993
# then cycle:
cd ~/seaforward/hindcast
./run_hindcast_cycle.sh
# results: hindcast/model-runs/<CONFIG>/<T>/hcast/CROCO_FILES/croco_his.nc
```