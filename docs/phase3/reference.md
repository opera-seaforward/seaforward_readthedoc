```bash
source ~/seaforward/env.sh
source ~/seaforward/forecast/track.sh
conda activate seaforward
cd ~/seaforward/forecast
./run_forecast_today.sh
# 2-day spin-up → 5-day forecast (init from spin-up end)
# result: forecast/model-runs/<CONFIG>/<date>/fcst/CROCO_FILES/croco_his.nc
```
!!! note
    **Next:** Phase 4 — *Running a Hindcast*, which reuses Phase 2's steps and swaps the data source (GLORYS + GFS) for a past period.