# Phase 6 — Validation

Phase 5 showed you how to look at a run. This chapter is about deciding whether to
believe it — DCC process **V1**.

Most of the work is not computing statistics — it is choosing what to compare against. A
model that agrees with the product that supplied its boundaries has shown consistency,
not skill. A model that disagrees with a coarse reference may be resolving something the
reference cannot see. Both mistakes produce a number that looks like an answer.

Everything on this chapter's pages is one engine, `sftools.validation` (plus
`sftools.validation_composite` for the multi-cycle case), reused four ways:

| Where | Cycles | Interface |
| --- | --- | --- |
| `notebooks/02_validation.ipynb` | one | interactive, Sections 1–10 |
| `notebooks/03_composite_validation.ipynb` | several, merged by **lead time** | interactive 

So the chapter is organised around the questions.

| The question | What answers it | Page |
| --- | --- | --- |
| Is what came out of C1 even trustworthy to look at? | grid/time sanity check, NaN/overflow check, reference-product availability | The references |
| How close is the forecast to the product it was downscaled from? | bias maps, scatter, Taylor diagram, GODAE scorecard | Against an analysis |
| What does the vertical structure of the agreement look like? | point/full-domain profiles, error-vs-depth, 4-level depth comparison | Below the surface |
| How close is the forecast to what was actually observed? | satellite SST/SSS (gridded), optional in-situ (class 4, per depth layer) | Against observations |
| Did the cycle pass or fail, and by how much margin? | automated pass/fail summary, HTML report, single-cycle and composite | Forecast skill |
| How do I do this for my own configuration? | env vars, single vs. composite, headless/batch | Doing this for your own run |

## A reference is not the truth

Every product here is an observation with its own error, an analysis that assimilated observations into a model, or a statistical reconstruction. Two consequences run through the chapter.
**Comparing against your own forcing measures consistency.** Mercator supplied this run's
initial and boundary conditions, so agreement is partly guaranteed. Worth doing — it
catches a downscaling that has gone somewhere strange — but it cannot show the forecast is
good.                                                           
**Comparing a fine model against a coarse reference penalises resolution.** An eddy the
model resolves at 9 km and a 0.25° product renders as a smear counts as error even when
the model has it right. This is the **double penalty**.
Both are why the chapter uses several references rather than one. Where two independent
products agree about the model, that agreement is worth more than either number alone. 

## The references                                               
| Reference | What it is | Best for |
|---|---|---|
| **OSTIA** | L4 SST analysis, 0.05°, gap-free | SST maps and error growth |
| **ODYSSEA** | L3S merged satellite SST, 0.1°, cloud gaps | SST skill, independent of in-situ |
| **SMOS** | L4 merged satellite SSS, 0.125°, gap-free | satellite SSS validation |
| **DUACS** | L4 altimetry, 0.125° | sea level, heavily smoothed |
| **GlobCurrent** | total surface current, 0.25°, 0 m and 15 m | currents — total flow, not geostrophic only |
| **ARMOR3D** | reconstructed T, S, SSH, MLD, 1/8°, 50 levels | the subsurface |
| **Mercator / GLORYS** | the parent product, 0.083° | consistency, and as a competitor in the skill comparison |
| **In-situ TAC** | in-situ observations (profiles, trajectories, Argo, etc) | validation against in situ |  


!!! tips "Two notebooks, one merging rule"
    `02_validation.ipynb` validates **one** cycle, indexed by calendar date.
    `03_composite_validation.ipynb` merges **several** cycles, indexed by
    **forecast lead time** instead (`sp1`, `sp2` = spin-up days; `fcst1`,
    `fcst2`, ... = forecast lead day 1, 2, ...). A cycle that doesn't reach a
    given lead is simply skipped for that lead, so cycles of different length
    composite together cleanly. Every page in this chapter applies to both —
    where the two diverge, it says so.

`Yorig` is required: a CROCO file written without CF time units carries raw seconds, and
without a reference year the download would silently request the wrong decade. 2000 for
the forecast track, 1993 for hindcasts.

In the two notebooks, all five download through one call, sized to the run being validated — it reads the run's
dates and grid and fetches only that.

Firstly check the availability of the product online before process to the downloading.

```python
AVAIL = {
    name: cmems.dataset_available(name)
    for name in ("mercator_forecast", "ostia_l4", "odyssea_l3s", "smos_l4_sss")
}
```

```text
Fetching catalogue 1:   0%|               | 0/2 [00:00<?, ?it/s]
Fetching products:   0%|                  | 0/1 [00:00<?, ?it/s]
Fetching products: 100%|██████████| 1/1 [00:00<00:00,  1.85it/s]
Fetching catalogue 1:  50%|███▌   | 1/2 [00:02<00:02,  2.57s/it]
  CMEMS product 'mercator_forecast' (cmems_mod_glo_phy_anfc_0.083deg_P1D-m): available

Fetching catalogue 1: 100%|███████| 2/2 [00:05<00:00,  2.54s/it]
                                                                
Fetching catalogue 1:  50%|███▌   | 1/2 [00:02<00:02,  2.29s/it]
  CMEMS product 'ostia_l4' (METOFFICE-GLO-SST-L4-NRT-OBS-SST-V2): available
Fetching catalogue 1: 100%|███████| 2/2 [00:04<00:00,  2.37s/it]

Fetching products:   0%|                  | 0/1 [00:00<?, ?it/s]
Fetching products: 100%|██████████| 1/1 [00:00<00:00,  1.83it/s]
Fetching catalogue 1: 100%|███████| 2/2 [00:02<00:00,  1.14s/it]
  CMEMS product 'odyssea_l3s' (IFREMER-GLOB-SST-L3-NRT-OBS_FULL_TIME_SERIE): available
Fetching catalogue 1:   0%|               | 0/2 [00:00<?, ?it/s]
Fetching products:   0%|                  | 0/1 [00:00<?, ?it/s]
Fetching products: 100%|██████████| 1/1 [00:00<00:00,  1.91it/s]
Fetching catalogue 1: 100%|███████| 2/2 [00:02<00:00,  1.13s/it]
  CMEMS product 'smos_l4_sss' (cmems_obs-mob_glo_phy-sss_nrt_multi_P1D): available
```
