# Setup

This section initializes the Python environment and imports the necessary modules from the `sftools` toolkit.

- `sftools.postprocess` (imported as `pp`) handles loading CROCO outputs, extracting variables, computing derived fields (like speed or vorticity), and managing the vertical sigma-to-depth coordinate transformations.
- `sftools.plotting` (imported as `pl`) provides a smart, high-level plotting wrapper to easily generate standardized maps, cross-sections, and profiles.
- `sftools.validation` (imported as `val`) includes statistical tools to compare CROCO high-resolution runs against parent datasets (such as Mercator or GLORYS).

_Note: The `importlib.reload()` calls are specifically useful in an interactive Jupyter Notebook environment. They ensure that any live modifications made to the `sftools` source code are immediately reflected without needing to restart the Python kernel._

```python
import importlib
import sftools
import sftools.postprocess as pp
import sftools.plotting    as pl
import sftools.animation as anim
import sftools.validation  as val
importlib.reload(anim)
importlib.reload(pp)
importlib.reload(pl)
```
