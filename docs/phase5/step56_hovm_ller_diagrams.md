# Hovmöller diagrams

- **Time vs Depth (`kind="time_depth"`)**: Perfect for visualizing the evolution of the water column stratification at a specific fixed point.
- **Time vs Latitude/Longitude (`kind="time_lat"` / `"time_lon"`)**: Useful for tracking the propagation of oceanic structures (like eddies, waves, or fronts) across a specific transect over time.


## salinity



```python
fig = pl.plot(pp.hovmoller(ds, "salt", "time_lat", lon0=-19))
```

Hovmöller diagrams display the temporal evolution of a variable along a single spatial dimension (either depth, latitude, or longitude) against time. 
Salinity is a major water mass tracer. The code below extracts the salinity field and plots it alongside bathymetric contours (isobaths) or as a vertical profile/section.

![Plot 27](../img/phase5/plot_27.png)


```python
fig = pl.plot(pp.hovmoller(ds, "salt", kind="time_depth", lon0=lon0, lat0=lat0))
```

![Plot 28](../img/phase5/plot_28.png)


## temperature



```python
fig = pl.plot(pp.hovmoller(ds, "temp", "time_lat", lon0=-19))
```

Water temperature is crucial for coastal dynamics (e.g., upwellings). Here is how to plot the temperature field to observe thermal gradients.

![Plot 29](../img/phase5/plot_29.png)


```python
fig = pl.plot(pp.hovmoller(ds, "temp", kind="time_depth", lon0=lon0, lat0=lat0))
```

![Plot 30](../img/phase5/plot_30.png)


## Speed



```python
fig = pl.plot(pp.hovmoller(ds, "speed", kind="time_depth", lon0=lon0, lat0=lat0))
```

Current velocity (magnitude) highlights areas of strong shear or dominant oceanic jets.

![Plot 31](../img/phase5/plot_31.png)


## Zonal current (u)



```python
fig = pl.plot(pp.hovmoller(ds, "u", kind="time_depth", lon0=lon0, lat0=lat0))
```

The zonal component represents the current flowing from West to East.

![Plot 32](../img/phase5/plot_32.png)


## Meridional current (v)



```python
fig = pl.plot(pp.hovmoller(ds, "v", kind="time_depth", lon0=lon0, lat0=lat0))
```

The meridional component represents the current flowing from South to North.

![Plot 33](../img/phase5/plot_33.png)

