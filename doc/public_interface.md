# Public Interface

Mixture of:
* the not too R specific parts of rprojroot (rest in separate module)
* the pyprojroot 0.2.0 interface
* the RootCriterion class

Outstanding issues:

* subdir: I believe can be emulated by providing path as a relative path, see
  also https://github.com/r-lib/rprojroot/issues/84 - revisit `has_basname`
  implementation.

## pyprojroot

How to set/manage the package's default root criterion?

Biggest challenge: make it easy to tailor a root criterion.

Measure performance...

## Missing Criteria:

* for regular expression, some subdir argument, where to search for the file/dir.
* pattern matching directories specifically
* a rule matching a dir or file's name with the directory's basename as a component,
  e.g. `<project>/<project>.Rproj` ...
* criteria testing absence of files... or generic negation?!
* add more predefined criteria closer to the python universe

## Observed use cases

Use https://github.com/search/advanced

There are projects out there importing here like this:

```python3
from pyprojroot.pyprojroot import here
```

```python3
import pyprojroot
PLOT_PATH = str(pyprojroot.here("reports/figures/test_plot.png"))
```

```python3
import pyprojroot
pyprojroot.here("data").joinpath("raw")
```

```python3
data_dir = pyprojroot.here('data')
```

Notebooks:

Frequently a funny mixture of `os.path` and `pathlib`,
sometimes a mixture of `pyprojroot` and `pyhere`

```python3
default_config_path = str(pyprojroot.here("configs"))
```

```python3
loc = pyprojroot.here('./data/to_match_special/' + subfolder)
zip_ej = pyprojroot.here('./data/outputs/ZCTA_EJ_special.csv')
```

## similar projects

Great inspiration for pyprojroot's here

https://pypi.org/project/pyhere/
https://github.com/wildland-creative/pyhere