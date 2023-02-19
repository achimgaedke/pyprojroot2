# About `pyprojroot2`

Want to determine where in the file system your project's base (or root) directory is?

`pyprojroot2` provides the solution, makes it easy to locate data in a project.

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
If the project root is not recognized, you can add a `.here` file into the
corresponding directory, helping `here` out.

Want to know what `pyprojroot2` chose and why?

```python3
from pyprojroot2 import get_root_desc

get_root_desc(here())
```

## Predefined root criteria

A variety of criteria are available in the submodule `predefined_roots`, e.g.

```python
from pyprojroot2.predefined_criteria import is_git_root

is_git_root.find_root()
```

This finds specifically the git repository project root.

The criterion `py_here_criteria` is used as default by `here` as it combines
many typical python project root criteria. It serves most python projects or
data-science notebook project out of the box.

## Define your own (root) criteria

If you know that your project root will have the (only) `data` directory in
your project, then you can specify:

```python
has_dir("data")
```

as a root criterion.

The operators `&` for logical and and `|` do work on any criterion,
adhering to python's operator precedence - in doubt use parentheses.

Unsurprisingly, the predefined `is_vcs_root` criterion is:

```python3
is_vcs_root = is_git_root | is_svn_root
```

```python3
from pyprojroot2 import as_root_criterion
from pyprojroot2.predefined_criteria import is_git_root, has_dir, is_here

my_root = is_git_root | is_here
my_data = my_root.find_root_file("data")
```

This root criterion will first look for a git root in all parent directories,
if that isn't found anywhere, then move on to finding a directory with a
`data` directory and finally if `data` couldn't be found, look out for `.here`.

If none of those could be located, then a `FileNotFoundError` exception
is raised.

If you know that the `data` directory is in the git root directory, you
could write:

```python3
my_root = (
    (is_git_root & has_dir("data")) |
    is_here,
)
```

and also keep the `.here` file marker as a fallback option.

## R-like interface

The modules `rprojroot` and `rhere` are python ports of the corresponding
R packages on top of the `pyprojroot2` core module. 

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
