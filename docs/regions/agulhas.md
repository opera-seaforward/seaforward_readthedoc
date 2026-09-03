The Agulhas retroflection region south of South Africa — one of the most energetic
western-boundary-current systems on Earth.

![Agulhas_12 grid and bathymetry](../img/agulhas_12_portrait.png)

| | |
|---|---|
| **Box** | 17°E–30°E, 38°S–32°S |
| **Resolution** | 1/12°, 50 σ-levels |
| **Hemisphere** | Eastern → `FIX_GFS_LON=0` |
| **Distinctive** | The Agulhas Current and its retroflection; a wide, mostly open-ocean domain with the coast running roughly east–west along the top |

**Physical notes.** The Agulhas is a **western boundary current** — fast, narrow and
deep, running south along the African coast before retroflecting back into the Indian
Ocean and shedding rings into the Atlantic. That makes it dynamically unlike either
Canary's eastern-boundary upwelling or IGOG's equatorial regime.

**Per-region gotchas.**

- **Fast currents mean a smaller timestep.** The Agulhas runs at around 2 m/s, among
  the strongest boundary currents anywhere, so the CFL condition may need a smaller
  `dt` than the 1/12° default. Watch the first steps and reduce `dt` if it blows up.
- **Steep bathymetry.** The Agulhas Bank and its sharp shelf break make the grid
  smoothing work harder — check the smoothing output settles near 0.2, and look at
  the bathymetry panel above for over-steepened cells.

This region is built end to end, with an AGRIF child, in **Phase 9**.