```
sftools/
├── postprocess.py    # loaders, extractors, derived fields, sigma->depth
├── define_attrs.py   # CF metadata + display defaults (single source of truth)
├── plotting.py       # attribute-driven plotting + smart plot() wrapper
└── validation.py     # model-vs-parent validation (maps, growth, profiles, ...)
```

The extractors return labelled `xarray.DataArray`s; the plotters read those
labels. Attributes drive labelling and colour; you override at plot time.
Depth is a uniform option (`depth_m=`) across maps, currents, time series and
error growth; profiles and sections span the full column. Time origins differ
by track (hindcast `Yorig=1993`, forecast `Yorig=2000`).