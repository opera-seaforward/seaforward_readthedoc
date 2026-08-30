**One cycle, today:**

```bash
source ~/seaforward/env.sh
source ~/seaforward/forecast/track.sh
conda activate seaforward
cd ~/seaforward/forecast
./run_forecast_cycle.sh
# 2-day spin-up → 5-day forecast (init from spin-up end)
# result: forecast/model-runs/<CONFIG>/<date>/fcst/CROCO_FILES/croco_his.nc
```

**Flags:**

```bash
./run_forecast_cycle.sh --tides                 # needs croco_plain_tides
./run_forecast_cycle.sh --rivers                # needs croco_plain_rivers
./run_forecast_cycle.sh --child 1way            # needs croco_1way
./run_forecast_cycle.sh --child 2way --tides    # needs croco_2way_tides
./run_forecast_cycle.sh --date 2026-07-11       # rerun a past cycle
```

**Binary name:** `croco_` + `plain|1way|2way` + `_tides` + `_rivers`, in that order.

**Detached run:**

```bash
nohup ./run_forecast_cycle.sh > fcst_$(date -u +%Y%m%d).log 2>&1 &
tail -f fcst_$(date -u +%Y%m%d).log
```

**Daily cron, 06:00 UTC:**

```
0 6 * * *  /bin/bash -lc 'source ~/seaforward/env.sh && cd ~/seaforward/forecast && ./run_forecast_cycle.sh >> ~/seaforward/forecast/cron.log 2>&1'
```