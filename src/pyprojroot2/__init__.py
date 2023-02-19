from .predefined_criteria import (
    has_dir,
    has_file,
    has_file_pattern,
    is_git_root,
    is_vcs_root,
    py_here_criteria,
    r_here_criteria,
)
from .pyprojroot_0_2_0 import here, py_project_root
from .root_criterion import RootCriterion, as_root_criterion
from .rprojroot import find_root, find_root_file, get_root_desc, is_root_criterion

# Purpose of this module:

# meet expections from https://rprojroot.r-lib.org/articles/rprojroot.html
# list of exports: https://github.com/r-lib/rprojroot/blob/main/NAMESPACE
# don't try to add everything here but rather a handy subset
# for a more complete rprojroot experience, use from pyrojroot2 import rprojroot

# provide `here`` and `py_project_root`` for compatibility wiht pyprojroot-0.2.0
# don't provide the interface of never published pyprojroot-0.3.0

# The r-here "here" functionality is available in the rhere module.
# use from pyrojroot2 import rhere
# https://here.r-lib.org/articles/here.html

# todo: how to link the version up to pyproject.toml?
# probably use setuptools_scm
__version__ = "0.4.0"

__all__ = [
    # pyprojroot-0.2.0
    "here",
    "py_project_root",
    # rprojroot
    "as_root_criterion",
    # "criteria", # todo: default criteria for this project
    "find_root",
    "find_root_file",
    "from_wd",
    "get_root_desc",
    "has_basename",
    "has_dir",
    "has_file",
    "has_file_pattern",
    "is_git_root",
    "is_root_criterion",
    "is_svn_root",
    "is_vcs_root",
    # that should be RootCriterion
    # "root_criterion",
    # pyprojroot2
    # core
    "RootCriterion",
    # other more pythonic prespecified criteria
    "py_here_criteria",
    "r_here_criteria",
    "__version__",
]
