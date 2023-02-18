# Origin / Refactor

This project is a complete rewrite of [Daniel Chen's pyprojroot](https://github.com/chendaniely/pyprojroot)
inspired by  the issues in the tracker and the `TODO`s in the code.

## Install

Try it out:

```shell
pip3 install git+https://github.com/achimgaedke/pyprojroot2.git@pyprojroot2-rewrite
```

It works as a drop in replacement for `pyprojroot`:

```python3
import pyprojroot2 as pyprojroot
```

The project runs with python-3.7 and upwards and no other dependencies
required.

## Use `here`

`here` is straight forward to use, simply find your directories relative to
your project:

```python3
from pyprojroot2 import here

data_path = here("data")

pd.read_csv(data_path / "dataset.csv")
```

The project is detected with the help of a (pythonic) set of criteria starting
from the current path, upwards in the filesystem.

Want the pathname as string? (It doens't come with a `/` at the end.)

```python3
data_path = str(here("data"))
```

If the current path is not somewhere inside the project you want to detect,
you can specify it:

```pyton3
data_path = here("data", path="/humungous/partion/some/note/book/file.ipynb")
```

If no root could be determined, the exception `FileNotFoundError` is raised.

Want to know what `pyprojroot2` chose and why?

```python3
from pyprojroot2 import find_root_with_reason

find_root_with_reason()
```

Todo: Outupt - test it!

## Predefined root criteria

A variety of criteria are available in the submodule `predefined_roots`.

```python
from pyprojroot2.predefined_roots import r_root_criterion

r_root_criterion.find_root()
```

This finds a project root like `rprojroot` does it.

The criterion `py_root_criterion` is used by `here` - and serves most python
projects or data-science notebook project out of the box.

## Define your own (root) criteria

Step 1:

Define your own filesystem based criteria using `has_file`,
`has_dir`, `has_file_pattern` or `match_glob` to create a project
criterion, which matches a specific project's filesystem structure, e.g.
`git` or a python package.

A criterion is soley testing a given directory whether it meets the
checks. A variety of criteria are available at `predefined_criteria`.

Step 2:

Bundle different project criteria together to a root criterion,
so if one isn't successful, the next one is searched for.

The root criterion does actually do the search of the filesystem for
the root of your project.

This is easy to elaborate in an example:

```python3
from pyprojroot2 import as_root_criterion
from pyprojroot2.predefined_criteria import is_git_root, has_dir

my_root = as_root_criterion(
    {
        "is_git": is_git_root,
        "has_data": has_dir("data"),
        "has_here_file": ".here", # will match any entry (file or dir)
    }
)

my_data = my_root("data")
```

This root criterion will first look for a git root in all parent directories,
if that isn't found anywhere, then move on to finding a directory with a
`data` directory and finally if `data` couldn't be found, look out for `.here`.

If none of those could be located, then a `FileNotFoundError` exception
is raised.

If you know that the `data` directory is in the git root directory, you
could write:

```python3
my_root = as_root_criterion(
    {
        "is_git_with_data": is_git_root & has_dir("data"),
        "has_here_file": ".here",
    }
)
```

Keeping the `.here` file as a fallback option.


The operators `&` for logical and and `|` do work on any criterion,
adhering to python's operator precedence - in doubt use parentheses.

Unsurprisingly, the predefined `is_vcs_root` criterion is:

```python3
is_vcs_root = is_git_root | is_svn_root
```

If you have only one criterion, then you can skip this step using the
convenience functions `find_root`, ... of criteria, doing this implicitly:

```python3
(is_git_vcs & has_dir("data")).find_root()
```

will find the root for this one criterion.

The root criteria can be manipulated using the OrderedDict methods:

```python3
del my_root["has_here_file"]
```

to remove a criterion or demote a criterion:

```
my_root.move_to_end("some_less_expected_criterion")
```

by moving it to the end.

## Use outside python

The command `pyprojroot2` will allow basic root finding operations on
the shell. So you can be sure, the result is consistent with the python
scripting.

This command prints out the (default) project root directory searched from the
current directory.

```shell
pyprojroot2
```

If no project root is found, it will fail with an error message.
