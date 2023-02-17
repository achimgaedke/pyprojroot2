# Public Interface

Pile of ideas, references, pointers...

## here

Another package, but based on pyprojroot?
No, a submodule, easily importable.

Missing:
* subdir: I believe can be emulated by providing path as a relative path
* make_fixed_file: use pathlib features

There are some extra commands, which might or might not need
a separate implementation, see `here.py`.

Is there an expectation of caching?

## pyprojroot

how to set the default root criterion?

Biggest challenge: make it easy to tailor a root criterion.
Second challenge: provide convenience and legacy functions at the correct location.

Consider using OrderedDict as base class, exposing methods to users.
Unnamed parameters will be automatically named and put into the dict at the
beginning.

Measure performance...

## Missing Criteria:

* for regular expression, some subdir argument, where to search for the file/dir.
* pattern matching directories, entries in general
* a rule matching a dir or file's name with the directory's basename as a component,
  e.g. `<project>/<project>.Rproj` ...
* criteria testing absence of files... or generic negation?!

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