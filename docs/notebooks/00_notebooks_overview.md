# notebooks/ — SEA-FORWARD Jupyter Notebook Toolkit

Guided, interactive pipeline owned by DCC processes **V1** (validation) and **D1** (downstream
post-processing, exercises, sensitivity analysis, animation).

``` { .text .no-copy }
notebooks/
├── 01_seaforward_postprocess_plot.ipynb  ← maps, sections, profiles, Hovmöller,
│                                            time series (D1)
├── 02_validation.ipynb                   ← single-cycle validation: bias maps,
│                                            scatter plots, Taylor diagrams, time
│                                            series, pass/fail summary, optional
│                                            in-situ scoring, HTML report, batch
│                                            history across cycles (V1)
├── 03_composite_validation.ipynb         ← multi-cycle validation, merged and
│                                            indexed by forecast LEAD TIME rather
│                                            than calendar date (V1)
├── 04_exercises.ipynb                    ← guided exercises: upwelling index,
│                                            MLD, coastal jet, eddy detection (D1)
├── 05_sensitivity.ipynb                  ← wind-forcing sensitivity study,
│                                            Step 5.3 (U3 -> C1 -> D1)
├── 06_animation.ipynb                    ← 5 animations built on a single entry
│                                            point, sftools.animation.animate()
│                                            (D1)
├── _paths.py                             ← shared helper, NOT a notebook — cycle
│                                            discovery + path resolution, see below
└── region_cells.py                       ← region-picker helper cells

sftools/
├── validation.py                 ← single module for every single-cycle validation
│                                    building block: bias maps, profiles, scatter,
│                                    GODAE scorecard/Taylor diagram, satellite
│                                    SST/SSS, optional in-situ, HTML summary
│                                    (imported as `val` in 02_validation.ipynb and
│                                    03_composite_validation.ipynb — some of that
│                                    module's docstrings/prose refer to logical
│                                    sub-areas as "validation_godae"/
│                                    "validation_satellite"; there is no separate
│                                    top-level module by either of those names)
├── validation_composite.py       ← lead-time compositing across cycles (imported
│                                    as `vc` in 03_composite_validation.ipynb only)
├── download/cmems.py             ← Copernicus Marine availability checks + downloads
│                                    (`from sftools.download import cmems`)
└── animation.py                  ← sftools.animation.animate() — the single entry
                                    point behind every animation in 06_animation.ipynb

```

