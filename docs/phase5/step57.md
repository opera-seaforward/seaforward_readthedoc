A few points that recur when validating a downscaled run against a coarser
parent:

**High SST/SSH correlation is good; lower current correlation is also good.** SST and SSH are smooth, large-scale fields — the model should reproduce the parent closely (correlations ~0.95). Currents are gradient-derived, chaotic and mesoscale — the high-resolution model adds eddies and filaments the coarse parent lacks, so a *moderate* correlation with a structured difference panel is the signature of downscaling **adding value**. Perfect agreement in the currents would mean the model added nothing.

**The difference panel shows where the model adds structure.** A near-white SST difference (large scales matched) with faint mesoscale wisps is a healthy result. Colourful current-difference dipoles usually mark slightly displaced jets/eddies — the "double penalty" of a feature that is present in both but not perfectly aligned; position matters more than magnitude.

**The surface differs most; agreement improves with depth.** See *error vs depth* above — this is expected and a good consistency check.

**The diurnal cycle causes oscillations in error growth.** CROCO output is sub-daily (e.g. 6-hourly) and carries a day/night SST cycle; the parent is a daily average. Comparing them directly makes the error oscillate once per day. Use `daily_mean=True` to average CROCO to daily means and get clean growth curves. (The oscillation itself reflects real sub-daily physics the daily reanalysis lacks — another downscaling value-add.)

**Sigma vs z-level in sections.** A CROCO section shows smooth, terrain-following bathymetry; the parent shows stair-stepped fixed depth levels. This contrast illustrates why regional models use sigma coordinates to represent the shelf and slope.