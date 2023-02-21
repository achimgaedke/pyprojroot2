import pathlib
import typing

from .core_criteria import RootCriterion, PathSpec
from .predefined_criteria import py_here_criteria
from .generic_criteria import HasFile, as_root_criterion

__all__ = ["here", "dr_here", "i_am", "set_here"]

# this module provides functions largely compatible with
# https://here.r-lib.org/articles/here.html

# also look at
# https://pypi.org/project/pyhere/
# https://github.com/wildland-creative/pyhere

# that's not a constant...
_rhere_root_criterion: RootCriterion = py_here_criteria


# https://github.com/r-lib/here/blob/970dd2726c5cddda4a0e44e910fe5290be063485/R/here.R#L33
# TODO: this actually uses a cached version of the root path
def here(*args: typing.Any, **kwargs: typing.Any) -> pathlib.Path:
    """
    Find a file relative to the project's root.
    """
    return _rhere_root_criterion.find_file(*args, **kwargs)


# https://github.com/r-lib/here/blob/970dd2726c5cddda4a0e44e910fe5290be063485/R/dr_here.R#L11
def dr_here(*args: typing.Any, **kwargs: typing.Any) -> str:
    """
    Give a reason why ``rhere`` choses a directory as root.
    """
    dir, reason = _rhere_root_criterion.find_root_with_reason(*args, **kwargs)
    return f"here() starts at {dir}\nThis directory {reason}"


# https://github.com/r-lib/here/blob/970dd2726c5cddda4a0e44e910fe5290be063485/R/here.R#L39
# actually not exported by r-here
def set_root_crit(criterion: RootCriterion) -> None:
    """
    Internal function to set the root criterion used by ``rhere``.

    Use ``i_am`` to set a new root criterion.
    """
    global _rhere_root_criterion
    _rhere_root_criterion = as_root_criterion(criterion)


# https://github.com/r-lib/here/blob/970dd2726c5cddda4a0e44e910fe5290be063485/R/set_here.R#L25
def set_here(path: PathSpec = ".") -> None:
    # warn: superseded: `i_am` is preferred!
    # add warning if alread exists...
    # and there's a verbose mode...
    (pathlib.Path(path) / ".here").touch()


# https://github.com/r-lib/here/blob/970dd2726c5cddda4a0e44e910fe5290be063485/R/i_am.R#L44
def i_am(
    path_or_criterion: typing.Any, uuid: typing.Optional[str] = None
) -> pathlib.Path:
    """
    Find the project root by checking existence of the test file.
    Alternatively, a root criterion can be used.

    If ``uuid`` is specfied, the uuid string is searched for in the file
    specified as first argument. See https://here.r-lib.org/articles/here.html#specify-a-unique-identifier
    for details.

    If successful this criterion is set as a new root criterion.

    Raises FileNotFoundError if no root was found.
    """
    root_criterion: RootCriterion
    if uuid is not None:
        root_criterion = HasFile(
            path_or_criterion, contents=str(uuid), fixed=True, n=100
        )
    else:
        # this will use HasFile for any string/path
        root_criterion = as_root_criterion(path_or_criterion)
    root_path = root_criterion.find_root()
    set_root_crit(root_criterion)
    return root_path
