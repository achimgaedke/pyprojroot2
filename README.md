# Origin / Refactor

This project is a complete rewrite of [Daniel Chen's pyprojroot](https://github.com/chendaniely/pyprojroot)
inspired the issues and looking at the `TODO`s in the code.

The fork moves the project forward to:

* compatibility with [rprojroot](https://github.com/r-lib/rprojroot) version 2
* compatibility with [here](https://github.com/r-lib/here)
* initially serve as drop in replacement of [pyprojroot](https://github.com/chendaniely/pyprojroot)
* tested support for python >=3.7
* aim for high test coverage
* bring the typing annotations and docstrings to a useful state (LSP, linters)
* (future) updated packging configuration/toolchain
* (future) distribution to pypi and conda as `pyprojroot2`
* (future) build up cookbook and reference documentation

## Useful commands

```shell
mamba env create -f environment-dev.yml
mamba env update -f environment-dev.yml  
```

```shell
PYTHONPATH=src python -m pytest --cov-report term-missing --cov=pyprojroot2  tests
python -m mypy src/pyprojroot2
```

See also the `Makefile`.