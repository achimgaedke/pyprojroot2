# Origin / Refactor

This project is a complete rewrite of [Daniel Chen's pyprojroot](https://github.com/chendaniely/pyprojroot)
inspired the issues and looking at the `TODO`s in the code.

## Install

Try it out,

```shell
pip3 install git+https://github.com/achimgaedke/pyprojroot2.git@pyprojroot2-rewrite
```

it should work as a drop in replacement for `pyprojroot`.

```python3
import pyprojroot2 as pyprojroot
```

The project runs with python-3.7 and upwards and no other dependencies
required.

## Use `here`

Ready to use, find your directories relative to your project:

```python3
from pyprojroot2 import here

data_path = here("data")
```

The project is detected with the help of a (pythonic) set of criteria starting
from the current path, upwards in the filesystem.

Want the pathname as string? (It doens't come with a ``/`` at the end.)

```python3
data_path = str(here("data"))
```

If the current path is not somewhere inside the project you want to detect,
you can specify it:

```pyton3
data_path = here("data", path="/humungous/partion/some/note/book/file.ipynb")
```

Want to know what ``pyprojroot2`` chose and why?

```python3
from pyprojroot2 import find_root_with_reason

find_root_with_reason()
```

If no root could be determined, the exception ``FileNotFoundError`` is raised.

## Predefined root criteria

A variety of criteria are available at ``predefined_roots``.

```python
from pyprojroot.predefined_roots import r_root_criterion

r_root_criterion.find_root()
```

This will find a project root like ``rprojroot`` would do it.

## Define your own root criteria

Step 1:

    Define your own filesystem based criteria using HasFile, HasDir,
    HasFilePattern to create a project criterion, which matches a
    specific project's filesystem signature, e.g. ``git``.

    A variety of criteria are available at ``predefined_criteria``.

Step 2:

    Bundle different project criteria together to a ``RootCriterion``,
    so if one isn't found, the next one is searched for.

This is even simpler in an example:

```python3
from pyprojroot2 import as_root_criterion
from pyprojroot2.predefined_criteria import is_git_root, has_dir`

my_root = as_root_criterion(
    is_git=is_git_root,
    has_data=has_dir("data"),
    has_here_file=".here", # will match any entry (file or dir)
)

my_data = my_root("data")
```

This root criterion will first look for a git root, if that isn't found,
then move on to finding a directory with a ``data`` directory and
finally if ``data`` couldn't be found, look out for ``.here``.

If none of those could be located, then a ``FileNotFoundError`` exception
is raised.

If you know that the ``data`` directory is in the git root directory, you
could write:

```python3
my_root = as_root_criterion(
    is_git_with_data=is_git_root & has_dir("data"),
    has_here_file=".here",
)
```

Keeping the ``.here`` file as a fallback option.

The operators ``&`` for logical and and ``|`` do work on any criterion,
adhering to python's operator precedence - in doubt use parentheses.

Unsurprisingly, the predefined ``is_vcs_root` criterion is:

```python3
is_vcs_root = is_git_root | is_svn_root
```

If you have only one criterion, then you can skip this step using the
convenience functions `find_root`, ... of criteria, doing this implicitly:

```python3
(is_git_vcs & has_dir("data")).find_root()
```

will find the root for this one criterion.

## Use outside python

The command ``pyprojroot2`` will allow basic root finding operations on
the shell. So you can be sure, the result is consistent with the python
scripting.

This command prints out the (default) project root directory searched from the
current directory.

```shell
pyprojroot2
```

If no project root is found, it will fail with an error message.

## Reference documentation

More to come... Here some pointers:

* the "machinery" is in `criteria.py` and `root.py`,
* the files `predefined_criteria.py` and `predefined_roots.py` provide criteria definitions ported from `rprojroot` and `pyprojroot`
* the files `__init__.py`, `root.py` and `here.py` should contain the "public interface",

The main distinction is to be made between:

* Criterion: tests a given directory, provides a reason for a match and allows combining with `&` (and) and `|` (or). Concrete examples are: `HasDir(".git")`, `HasFile("setup.cfg")`, ...
* RootCriteria: tests a list of criteria and uses the first criterion returning a match on one of the parent directories, e.g. typical RootCriteria for a python data-science project or an R project.

So far, I've written and tested the "machinery". Now I have to write the documentation
to see how the public interface should look like.

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
