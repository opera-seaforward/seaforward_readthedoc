# Phase 5 — Post-processing

<!-- <img src="../img/phase5.png" alt="Phase 5" style="width: 100%; height: 550px; object-fit: contain;" /> -->

![Phase 5](../img/phase5.jpeg)

SEA-FORWARD includes a small, self-contained Python toolkit for analysing CROCO
output — maps, sections, profiles, Hovmöller diagrams, time series and animations.
Comparing a run against the parent product it was downscaled from is the next
chapter, Validation.

The toolkit lives in `sftools/` and this chapter uses three of its modules:

| Module | Purpose |
| --- | --- |
| `postprocess.py` | Load CROCO output; extract fields, sections, profiles and time series; compute derived quantities (speed, vorticity, EKE) at the surface or any depth. |
| `define_attrs.py` | One registry of CF metadata **and** display defaults — colormap, range — for every variable. Plots label and colour themselves from this. |
| `plotting.py` | Attribute-driven plotting: generic builders plus a `plot()` wrapper that detects the plot type from the data. |

The design is a clean split:

- **Extractors** in `postprocess` build a labelled `xarray.DataArray`. They decide
  *what* — which variable, which depth, which time.
- **Plotters** in `plotting` decide *how* it looks, reading the labels from the data
  by default.

So a typical call reads:

```python
pl.plot(pp.field(ds, "temp", depth_m=50))
```

![Temperature at 50 m](../img/phase5_temp_50m.png)

The extractor builds temperature at 50 m; the plotter draws and labels it — the title,
the colour scale, the units and the depth all come from the data's own attributes.
Those two functions cover most of this chapter: `pp.field()` for the data,
`pl.plot()` for the figure.
<div style="display:flex; justify-content:center; margin:10px 0 14px 0;">
   <a href="https://raw.githubusercontent.com/opera-seaforward/seaforward_readthedoc/main/docs/notebooks/01_seaforward_postprocess_plot.ipynb" data-download-url="https://raw.githubusercontent.com/opera-seaforward/seaforward_readthedoc/main/docs/notebooks/01_seaforward_postprocess_plot.ipynb" data-download-filename="01_seaforward_postprocess_plot.ipynb" onmouseover="this.style.transform='scale(1.08)'; this.style.boxShadow='0 10px 24px rgba(0,0,0,0.18)';" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none';" style="display:inline-flex; align-items:center; justify-content:center; gap:16px; min-width: 80px; padding:20px 20px; border-radius:10px; background:linear-gradient(to bottom, #ffffcc 0%, #f4f797de 100%); color:#000000; text-decoration:none; font-size:1.2rem; line-height:1.1; text-align:center; transition:transform 0.18s ease, box-shadow 0.18s ease; transform-origin:center;">
      <img src="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/download.svg" alt="" aria-hidden="true" style="width:25px; height:25px; color:#000000; font-weight:bold filter:invert(1);" />
      <span>Download notebook 01_seaforward_postprocess_plot.ipynb</span>
   </a>
</div>
