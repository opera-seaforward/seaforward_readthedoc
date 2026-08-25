This is exactly what you produced at the end of Phase 2: a compiled model in
`forecast/scratch/<CONFIG>/`, with `croco.in` pointed at the dated
`croco_ini_*`/`croco_bry_*` files and the `for_croco/` forcing, run once with
`./croco croco.in`. If you want to repeat that single run:

```bash
source ~/seaforward/env.sh
source ~/seaforward/forecast/track.sh
export CONFIG_NAME=Canary_12
export FCAST=${CROCO_RUNS_ROOT}/${CONFIG_NAME}     # forecast/scratch/Canary_12
cd ${FCAST}
conda deactivate                                    # run outside conda
./croco croco.in 2>&1 | tee run.log | tail -60
```

The figure below illustrates how the forecast runs.
<figure style="text-align: center; margin: 20px 0;">
  <img src="../../img/model_C1.png" alt="Core forecasting-engine workflow" style="max-width: 100%; height: auto;">
  <figcaption style="font-size: 1em; color: #555; margin-top: 8px; font-style: italic;">
    Core forecasting-engine workflow combining <code>model_grid.nc</code>, <code>ocean-model-obc-input</code>, <code>ocean-model-init-input</code>, <code>river-upstr-input</code>, <code>atm-upstr-input</code>, and <code>tides-upstr-input</code>, run through the workflow-model-engine (CROCO-model, configuration, result-control, workflow-CROCO-monitor) and Ocean-output-manager (grid-transformation &rarr; format-converter &rarr; catalog-insertion), producing the ocean-model output linked to V1 and D1.
  </figcaption>
</figure>

!!! check
    ✅ It ends with `MAIN: DONE` and writes `CROCO_FILES/croco_his.nc` and `croco_avg.nc`. (The `IEEE_UNDERFLOW` note at the very end is harmless.)

That single run is one continuous simulation with **no separate spin-up** — you
set its `time_stepping`, `initial`, `boundary`, and `online` lines by hand in
Phase 2. It proves the configuration works. The operational cycle below does the
proper two-phase spin-up + forecast for you, automatically, every day — so from
here on you use **Part B**, not the manual edits.