# Phase 6 — Validation

Phase 5 showed you how to look at a run. This chapter is about deciding whether to
believe it.

Most of the work is not computing statistics — it is choosing what to compare against. A
model that agrees with the product that supplied its boundaries has shown consistency,
not skill. A model that disagrees with a coarse reference may be resolving something the
reference cannot see. Both mistakes produce a number that looks like an answer.

So the chapter is organised around the questions.

| The question | What answers it | Page |
|---|---|---|
| How close is the forecast to what was observed? | collocation against satellite observations | Against observations |
| Is the forecast worth running? | comparison with persistence and with the parent | Forecast skill |
| Does the field look right? | maps and differences against a gridded analysis | Against an analysis |
| Is the interior right, not just the surface? | profiles, sections, error against depth | Below the surface |
| How do I do this for my own run? | paths, downloads, other regions, new references | Doing this for your own run |

## A reference is not the truth

Every product here is an observation with its own error, an analysis that assimilated
observations into a model, or a statistical reconstruction. Two consequences run through
the chapter.

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
| **DUACS** | L4 altimetry, 0.125° | sea level, heavily smoothed |
| **GlobCurrent** | total surface current, 0.25°, 0 m and 15 m | currents — total flow, not geostrophic only |
| **ARMOR3D** | reconstructed T, S, SSH, MLD, 1/8°, 50 levels | the subsurface |
| **Mercator / GLORYS** | the parent product | consistency, and as a competitor in the skill comparison |

All five download through one call, sized to the run being validated — it reads the run's
dates and grid and fetches only that:

```bash
mkdir -p ~/seaforward/data/OBS
cd ~/seaforward
python3 << 'PYEOF'
import sftools.validation_obs as vo

HIS = 'forecast/model-runs/Canary_12/20260711/fcst/CROCO_FILES/croco_his.nc'
OBS = '~/seaforward/data/OBS'

for src in ('ostia', 'odyssea', 'duacs', 'globcurrent', 'armor3d'):
    print(vo.download_obs(HIS, src, OBS, Yorig=2000))
PYEOF
```

```text
ostia: METOFFICE-GLO-SST-L4-NRT-OBS-SST-V2
  2026-07-10 .. 2026-07-17   lon -22.65..-14.85  lat 13.44..24.54
  note: foundation SST — the temperature below the diurnal warm layer, so a
        midday model SST can read warmer without being wrong
/home/you/seaforward/data/OBS/ostia_2026-07-10_2026-07-17.nc
```

The filename carries the window, so a second cycle does not overwrite the first. Mercator
needs no download — the driver already fetched it for each cycle, beside the run.

`Yorig` is required: a CROCO file written without CF time units carries raw seconds, and
without a reference year the download would silently request the wrong decade. 2000 for
the forecast track, 1993 for hindcasts.

## What this chapter reports

The examples come from three consecutive Canary_12 forecast cycles in July 2026 — 11, 12
and 13 July, each a two-day spin-up and a five-day forecast. Three cycles is enough to see
whether a result is consistent, not enough to average confidently, so the figures show the
individual cycles rather than a confidence band.

Three findings:

- **Against independent SST observations, SEA-FORWARD is substantially closer than its
  parent** — 0.79 °C against Mercator's 1.16 °C at five days, and closer at every lead.
- **Against Mercator it is also better for the northward current** at every lead but the
  last. Against persistence it is level for currents and slightly worse for SST — the
  ocean surface changes slowly enough that assuming nothing changed is a strong baseline
  at these lead times.
- **Two independent SST products agree about the model.** ODYSSEA, which assimilates
  nothing, gives essentially the same numbers as OSTIA, which assimilates in-situ data —
  which is what makes the first finding credible.

!!! important
    This is three cycles of one configuration over one region in one month, not a statement about the system in general. What transfers is the method: every figure here regenerates for your own domain with the same few commands.