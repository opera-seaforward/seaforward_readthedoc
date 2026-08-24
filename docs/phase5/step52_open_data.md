# Open data

This section demonstrates how to load CROCO netCDF output files into memory using the `sftools` toolkit. We use `pp.open_history()` and specify the path to our `croco_his.nc` file. 

**Important Note on `Yorig`**: CROCO stores time as seconds since a reference year. For the hindcast track, this is typically `1993`. For the forecast track, it is `2000`. You must specify the correct `Yorig` when opening the file to decode the dates properly into Python `datetime` objects.

```python
H = "hindcast/model-runs/Canary_12/20251225/hcast/CROCO_FILES/croco_his.nc"
ds = pp.open_history(H, Yorig=1993)
```

### Parameters

Here, we define several common parameters that will be reused across multiple plots in the following sections:
- `depth`: The specific depth in meters (e.g., 1000m) to extract for horizontal slices.
- `lon0, lon1, lat0, lat1`: The coordinates defining the geographical start and end points of our vertical sections.
- `isobaths`: A list of depths (in meters) to draw as bathymetric contours on the maps.

```python
depth = 1000
lon0, lat0, lon1, lat1 = -21, -16, 21, 21
isobaths = [100, 200, 500, 1000, 2000]
```
