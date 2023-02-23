# About `pyprojroot2`

Want to determine where in the file system your project's base (or root) directory is?

`pyprojroot2` provides the solution, and makes it easy to locate data in a project.

This project is a complete rewrite of [Daniel Chen's pyprojroot](https://github.com/chendaniely/pyprojroot)
inspired by the issues in the tracker and the `TODO`s in the code.

## tl;dr

Sick of fiddling around with the current directory and searching for the correct
path to your data in your git project?

```python3
from pyprojroot2 import is_git_root
data_file = is_git_root.find_file("data/your_file.csv")
```

searches upwards from your current directory for the git root and
returns the absolute path name to your data file.

Many other popular project root criteria are available at
`pyprojroot2.predefined_roots`.

**Popular Choice:** `here("data/your_file.csv")` is a handy shortcut to
locate your data by detecting the root of a collection of python projects.

## Install

Try it out:

```shell
pip3 install git+https://github.com/achimgaedke/pyprojroot2.git
```

It works as a drop-in replacement for `pyprojroot`:

```python3
import pyprojroot2 as pyprojroot
```

The project runs with python-3.7 and upwards and no other dependencies
required.

## Use `here`

`here` is straightforward to use, simply find your files relative to
the project's root (or base) directory:

```python3
from pyprojroot2 import here

data_path = here("data")

pd.read_csv(data_path / "dataset.csv")
```

The project is detected with the help of a (pythonic) set of criteria starting
from the current path, upwards in the filesystem.

Want the pathname as a string?

```python3
data_path = str(here("data"))
```

If the current directory is somewhere outside the project you want to detect,
you can specify the start path for the search:

```pyton3
data_path = here("data", path="/humungous/partiton/some/notebooks/")
```

If the root could not be determined, the exception `FileNotFoundError` is raised.

In that case, you can add a `.here` file into the corresponding directory,
giving `here()` a hint or define your root criteria, as described in the
next section.

Want to know what `here()` chose as root and why?

```python3
from pyprojroot2 import get_root_desc, py_here_criteria

get_root_desc(py_here_criteria, here())
```

Under the hood `here()` uses the `py_here_criteria` predefined criterion,
bundling a popular selection of project root criteria.

More functions comparable to the R packages `rprojroot` and `here` are available
from the `pyprojroot2` submodules `rprojroot` and `rhere`.

## Define your root criteria

If you know that your project root will have the (only) `data` directory in
your project, then you can specify:

```python
has_dir("data")
```

as a root criterion.

You can combine root criteria using the operators `&` (logical "and") and
`|` (logical "or"). Unsurprisingly, the predefined `is_vcs_root` criterion is:

```python3
is_vcs_root = is_git_root | is_svn_root
```

```python3
from pyprojroot2 import is_git_root, has_dir, is_here

is_my_root = is_git_root | is_here
my_data = is_my_root.find_root_file("data")
```

This root criterion will first look for a git root in all parent directories,
if that isn't found anywhere, then move on to finding a directory with a
`data` directory and finally if `data` couldn't be found, look out for `.here`.

If none of those could be located, a `FileNotFoundError` exception is raised.

If you know that the `data` directory is in the git root directory, you
could write:

```python3
is_my_root = (
    is_git_root & has_dir("data") |
    is_here
)
```

and also keep the `.here` marker file as a fallback option.

The usual operator precedence applies, `&` binds stronger than `|`.

## Use outside python

The command `pyprojroot2` will allow locating the root of a project on
the shell. So you can be sure, the result is consistent with the python
scripting.

This command prints out the project root directory searched from the
current directory using the default criteria

```shell
pyprojroot2
```

If no project root is found, it will fail with an error message.

Optionally you can set one of the predefined criteria with ``-c`` or
specify the start path.
