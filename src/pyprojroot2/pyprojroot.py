import warnings
from .here import here

warnings.warn(
    "Importing legacy module `pyprojroot2.pyprojroot`. Please use `from pyprojroot2 import here` or similar.",
    DeprecationWarning,
)

__all__ = ["here"]
