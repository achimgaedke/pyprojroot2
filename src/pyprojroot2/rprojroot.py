import pathlib
import typing

from .predefined_criteria import (
    from_wd,
    has_basename,
    has_dir,
    has_file,
    has_file_pattern,
    is_drake_project,
    is_git_root,
    is_pkgdown_project,
    is_projectile_project,
    is_r_package,
    is_remake_project,
    is_rstudio_project,
    is_svn_root,
    is_testthat,
    is_vcs_root,
    r_criteria,
)
from .core_criteria import PathSpec, RootCriterion
from .generic_criteria import as_root_criterion

# the rprojroot package actually doesn't have a default criterion and the
# criteria in the r package are rather a table of contents like list, not
# a criterion
criteria = r_criteria


# https://github.com/r-lib/rprojroot/blob/49a1a644246abcdcbe11a9396b1bb147d0919853/R/root.R#L89
def find_root(criterion: typing.Any, path: PathSpec = ".") -> pathlib.Path:
    return as_root_criterion(criterion).find_root(path)


# https://github.com/r-lib/rprojroot/blob/c5a32458701c7a951158d96618cfc07ed692d75f/R/file.R#L36
def find_root_file(
    *args: PathSpec, criterion: typing.Any, **kwargs: typing.Any
) -> pathlib.Path:
    return as_root_criterion(criterion).find_file(*args, **kwargs)


# https://github.com/r-lib/rprojroot/blob/49a1a644246abcdcbe11a9396b1bb147d0919853/R/root.R#L143
def get_root_desc(criterion: typing.Any, path: PathSpec) -> str:
    root_criterion = as_root_criterion(criterion)
    success, reason = root_criterion.test_with_reason(path)
    if success:
        return reason
    raise FileNotFoundError(f"path is not a root for {root_criterion.describe()}")


def is_root_criterion(criterion: typing.Any) -> bool:
    return isinstance(criterion, RootCriterion)


# and the shortcuts
# https://github.com/r-lib/rprojroot/blob/main/R/shortcut.R

# find_rstudio_root_file(..., path = ".")
find_rstudio_root_file = is_rstudio_project.find_file

# find_package_root_file(..., path = ".")
find_package_root_file = is_r_package.find_file

# find_remake_root_file(..., path = ".")
find_remake_root_file = is_remake_project.find_file

# find_testthat_root_file(..., path = ".")
find_testthat_root_file = is_testthat.find_file

__all__ = [
    # https://github.com/r-lib/rprojroot/blob/main/NAMESPACE
    # S3method("|",root_criterion)
    # S3method(as_root_criterion,character)
    # S3method(as_root_criterion,default)
    # S3method(as_root_criterion,root_criterion)
    # S3method(format,root_criterion)
    # S3method(print,root_criterion)
    # S3method(str,root_criteria)
    "as_root_criterion",
    "criteria",  # these are the actual R criteria!
    "find_package_root_file",
    "find_remake_root_file",
    "find_root",
    "find_root_file",
    "find_rstudio_root_file",
    "find_testthat_root_file",
    "from_wd",
    "get_root_desc",
    "has_basename",
    "has_dir",
    "has_file",
    "has_file_pattern",
    "is_drake_project",
    "is_git_root",
    "is_pkgdown_project",
    "is_projectile_project",
    "is_r_package",
    "is_remake_project",
    "is_root_criterion",
    "is_rstudio_project",
    "is_svn_root",
    "is_testthat",
    "is_vcs_root",
    # todo: how to link up to RootCriterion?
    # "root_criterion",
]
