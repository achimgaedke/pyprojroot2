# Origin / Refactor

This project is a complete rewrite of [Daniel Chen's pyprojroot](https://github.com/chendaniely/pyprojroot)
inspired the issues and looking at the `TODO`s in the code.

The fork moves the project forward to:

* initially serve as drop in replacement of [pyprojroot](https://github.com/chendaniely/pyprojroot)
* compatibility with [rprojroot](https://github.com/r-lib/rprojroot) version 2
* compatibility with [here](https://github.com/r-lib/here)
* tested support for python >=3.7
* aim for high test coverage
* bring the typing annotations and docstrings to a useful state (LSP, linters)
* (future) updated packging configuration/toolchain
* (future) distribution to pypi and conda as `pyprojroot2`
* (future) build up cookbook and reference documentation

## Install

Try it out,

```shell
pip3 install git+https://github.com/achimgaedke/pyprojroot2.git@pyprojroot2-rewrite
```

it should work as a drop in replacement for `pyprojroot`.

```python2
import pyprojroot2 as pyprojroot
```

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

## Documentation / Public interface...

More to come... Here some pointers:

* the "machinery" is in `criteria.py` and `root.py`,
* the files `predefined_criteria.py` and `predefined_roots.py` provide criteria definitions ported from `rprojroot` and `pyprojroot`
* the files `__init__.py`, `root.py` and `here.py` should contain the "public interface",

The main distinction is to be made between:

* Criterion: tests a given directory, provides a reason for a match and allows combining with `&` (and) and `|` (or). Concrete examples are: `HasDir(".git")`, `HasFile("setup.cfg")`, ...
* RootCriteria: tests a list of criteria and uses the first criterion returning a match on one of the parent directories, e.g. typical RootCriteria for a python data-science project or an R project.

So far, I've written and tested the "machinery". Now I have to write the documentation
to see how the public interface should look like.
