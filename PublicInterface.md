# here

another package, but based on pyprojroot

Missing: make_fixed_file
subdir functions

Understand: how to return when no root found
How to describe?!

subdir: I believe can be emulated by providing path as a relative path
make_fixed_file: use pathlib features


# pyprojroot

for criteria

base class root_criterion

method
find_file()


new criteria

has_license <- has_file("LICENSE")
is_projecttemplate_project <- has_file("config/global.dcf", "^version: ")


You can also combine criteria via the | operator:
is_r_package | is_rstudio_project

needs to fullfill all criteria

for RootCriterion: coerce strings to `HasEntry`

biggest challenge: make it easy to tailor a root criterion.


# Other Criteria:

pattern matching directories

# known use cases

https://github.com/search/advanced

There are projects out there importing here like this:
```
from pyprojroot.pyprojroot import here
```

```
import pyprojroot
PLOT_PATH = str(pyprojroot.here("reports/figures/test_plot.png"))
```

```
import pyprojroot
pyprojroot.here("data").joinpath("raw")
```

```
data_dir = pyprojroot.here('data')
```

always a funny mixture of os.path and pathlib


default_config_path = str(pyprojroot.here("configs"))

```
    loc = pyprojroot.here('./data/to_match_special/' + subfolder)
    zip_ej = pyprojroot.here('./data/outputs/ZCTA_EJ_special.csv')
```

# similar projects

Great inspiration for pyprojroot's here

https://pypi.org/project/pyhere/
https://github.com/wildland-creative/pyhere