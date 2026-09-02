Same ritual as always, on the **forecast** track:

```bash
source ~/seaforward/env.sh
source ~/seaforward/forecast/track.sh
conda activate seaforward
```

Set the child's variables. The child covers **nearly the same region** as the parent,
at **finer resolution** and with **more vertical levels**:

```bash
export CONFIG_NAME=Canary_25
export CONFIG_DIR=${CROCO_CONFIGS_ROOT}/${CONFIG_NAME}     # forecast/configs/Canary_25
export FCAST=${CROCO_RUNS_ROOT}/${CONFIG_NAME}             # forecast/scratch/Canary_25
export CF=${FCAST}/CROCO_FILES
mkdir -p ${CF} ${FCAST}/downloaded_data/PARENT
```

!!! note
    **Why the child sits inside the parent.** A nested child's open boundaries are filled by interpolating the parent's data, so the parent must **surround** the child — the interpolator needs parent data slightly *beyond* every child edge. That is why the child box is a touch smaller rather than exactly equal. You could instead keep the same box and pad the parent outward, but shrinking the child is the cleaner and more standard practice: every child boundary point then lands on real parent data, never extrapolated.