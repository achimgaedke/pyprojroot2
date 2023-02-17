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

## Development Commands

```shell
mamba env create -f environment-dev.yml
mamba env update -f environment-dev.yml  
```

```shell
PYTHONPATH=src python -m pytest --cov-report term-missing --cov=pyprojroot2  tests
python -m mypy src/pyprojroot2
```

See also the `Makefile`.
