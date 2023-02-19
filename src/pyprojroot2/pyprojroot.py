# this is explicitly providing the 0.2.0 version's interface of pyprojroot
# and marked deprecated

import warnings

from .pyprojroot_0_2_0 import here, py_project_root

__all__ = ["here", "py_project_root"]

warnings.warn(
    "Importing legacy module `pyprojroot2.pyprojroot`.",
    DeprecationWarning,
)
