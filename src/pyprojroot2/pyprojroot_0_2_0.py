import pathlib
import typing
import warnings

from .root_criterion import PathSpec, as_root_criterion
from .predefined_criteria import py_here_criteria


# be backwards compatible to pyprojroot version 0.2.0:
# https://github.com/chendaniely/pyprojroot/blob/4f8578e2f29b80ea0148ced534087e79141180fe/pyprojroot/pyprojroot.py


def py_project_root(
    path: PathSpec, project_files: typing.Tuple[str, ...]
) -> pathlib.Path:
    root_criterion = as_root_criterion(project_files)
    return root_criterion.find_root(path)


def here(
    relative_project_path: PathSpec = ".",
    project_files: typing.Optional[typing.Tuple[str, ...]] = None,
    warn: bool = True,
) -> pathlib.Path:
    if project_files is None:
        root_criterion = py_here_criteria
    else:
        root_criterion = as_root_criterion(project_files)

    project_entry = root_criterion.find_root_file(relative_project_path)
    if warn and not project_entry.exists():
        warnings.warn(f"Path doesn't exist: {project_entry}")
    return project_entry
