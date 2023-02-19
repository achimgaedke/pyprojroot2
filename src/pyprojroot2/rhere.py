import pathlib
import typing

from .predefined_criteria import py_here_criteria
from .root_criterion import HasFile, PathSpec, RootCriterion, as_root_criterion

__all__ = ["here", "dr_here", "i_am", "set_root_crit", "set_here"]

# this module provides functions largely compatible with
# https://here.r-lib.org/articles/here.html

# also look at
# https://pypi.org/project/pyhere/
# https://github.com/wildland-creative/pyhere

HERE_ROOT_CRITERION: RootCriterion = py_here_criteria


# https://github.com/r-lib/here/blob/970dd2726c5cddda4a0e44e910fe5290be063485/R/here.R#L33
# TODO: this actually uses a cached version of the root path
def here(*args: typing.Any, **kwargs: typing.Any) -> pathlib.Path:
    return HERE_ROOT_CRITERION.find_root_file(*args, **kwargs)


# https://github.com/r-lib/here/blob/970dd2726c5cddda4a0e44e910fe5290be063485/R/dr_here.R#L11
def dr_here(*args: typing.Any, **kwargs: typing.Any) -> str:
    _, reason = HERE_ROOT_CRITERION.find_root_with_reason(*args, **kwargs)
    return reason


# https://github.com/r-lib/here/blob/970dd2726c5cddda4a0e44e910fe5290be063485/R/here.R#L39
# actually not exported by r-here
def set_root_crit(criterion: RootCriterion) -> None:
    global HERE_ROOT_CRITERION
    HERE_ROOT_CRITERION = as_root_criterion(criterion)


# https://github.com/r-lib/here/blob/970dd2726c5cddda4a0e44e910fe5290be063485/R/set_here.R#L25
def set_here(path: PathSpec) -> None:
    # see
    # warn: superseded: `i_am` is preferred!
    # add warning if alread exists...
    (pathlib.Path(path) / ".here").touch()


# https://github.com/r-lib/here/blob/970dd2726c5cddda4a0e44e910fe5290be063485/R/i_am.R#L44
def i_am(*args: typing.Any, **kwargs: typing.Any) -> pathlib.Path:
    """
    Find the project root by checking existence of the test file.
    If successful set this as a new root criterion.

    Raises FileNotFoundError if no root was found or the root did not feature
    the test file.
    """
    root_criterion = HasFile(*args, **kwargs)
    root_path = root_criterion.find_root()
    set_root_crit(root_criterion)
    return root_path
