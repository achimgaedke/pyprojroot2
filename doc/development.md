## Agenda

Agenda:

* initially serve as drop in replacement of [pyprojroot](https://github.com/chendaniely/pyprojroot)
* compatibility with [rprojroot](https://github.com/r-lib/rprojroot) version 2
* compatibility with [here](https://github.com/r-lib/here)
* tested support for python >=3.7
* aim for high test coverage
* bring the typing annotations and docstrings to a useful state (LSP, linters)
* (future) updated packging configuration/toolchain
* (future) distribution to pypi and conda as `pyprojroot2`
* (future) build up cookbook and reference documentation

## Create new criteria:

Use this template:

```python3
from pyprojroot2.criteria import Criterion, PathSpec

class MyCriterion(Criterion):
    """
    Add some documentation about the file structure
    you want to match...
    """

    def __init__(self, some_params):
        self.property1 = some_params
        # and so on
        super().__init__()

    def is_met(self, path: PathSpec=".") -> bool:
        # your checking code here
        return True

    def describe(self) -> str:
        # customise the reason for meeting this criterion
        return f"My criterion working on `{self.property1}`"
```

When submitting as a pull request, make sure unittests are added.
The more generic/versatle or more likely used by many... the better.

## Development Commands

```shell
mamba env create -f environment-dev.yml
mamba env update -f environment-dev.yml  
```

```shell
PYTHONPATH=src python -m pytest --cov-report term-missing --cov=pyprojroot2  tests
python -m mypy src/pyprojroot2
```

The `Makefile` provides the `build`, `fmt` and `lint` targets.
