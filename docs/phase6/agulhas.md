The Agulhas retroflection region south of South Africa — one of the most energetic
western-boundary-current systems on Earth. Card to be filled in once the grid and
forecast are built.

!!! note
    **Notes for when it's built.** Box: **17°E–30°E, 38°S–32°S** (a wide, mostly open-ocean domain; the coast runs roughly E–W along the top, so axis-aligned — no rotation needed). Eastern hemisphere → `FIX_GFS_LON=0`. Two things to expect that differ from Canary/IGOG:

!!! important
    - **Fast currents → smaller timestep.** The Agulhas Current runs at ~2 m/s, one of the strongest western boundary currents on Earth. The CFL condition may require a **smaller `dt`** than the 1/12° default (watch the first steps; reduce `dt` if it blows up).
    - **Steep bathymetry.** The Agulhas Bank and the sharp shelf break mean the grid smoothing (`rfact`, `rx0`) works harder — check the smoothing output settles near 0.2, and eyeball the bathymetry portrait for over-steepened cells.